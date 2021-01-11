import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgres://postgres:admin@{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_get_questions_not_found(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        
    def test_delete_question(self):
        question = "What is the name of your first car?"
        answer = "Toyota Camry"
        category = 1
        difficulty = 1
        model = Question(question, answer, category, difficulty)        
        model.insert()
        # store the test question id
        id = model.id
        
        # total questions before delete
        total_questions = Question.query.count()
        res = self.client().delete(f'/questions/{id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(total_questions - 1, Question.query.count() )
        # query the question that was initially added
        deleted_question = Question.query.get(id)
        self.assertFalse(deleted_question)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Not found')
        self.assertFalse(data['success'])

    def test_create_question(self):
        data = {
            "question": "What is the name of your first car?",
            "answer" : "Toyota Camry",
            "category" : 1,
            "difficulty" : 1
        }

        res = self.client().post('/questions', json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], Question.query.count())

        # lets check if the question was inserted and is existing
        new_question = Question.query.get(data['question'])
        self.assertTrue(new_question)

    def test_create_question_bad_request(self):
        data = {
            "question": "What is the name of your first car?",
            "answer": "Toyota Camry",
            "category": 1
        }
        # count question before inserting
        oldest_count = Question.query.count()

        res = self.client().post('/questions', json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Bad Request')

        # lets check that the question did not insert after failing
        latest_count = Question.query.count()
        self.assertEqual(oldest_count, latest_count)

    def test_create_question_unproccessible(self):
        data = {
            "question": "What is the name of your first car?",
            "answer": "Toyota Camry",
            "category": 1,
            "difficulty": "hello"
        }
        # count question before inserting
        oldest_count = Question.query.count()

        res = self.client().post('/questions', json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Unprocessible')

        # lets check that the question did not insert after failing
        latest_count = Question.query.count()
        self.assertEqual(oldest_count, latest_count)

    def test_search_question(self):
        data = {
            "searchTerm": "Title",
        }

        res = self.client().post('/search', json=data)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_search_question_not_found(self):
        data = {
            "searchTerm": "zzzzzzzzzzz",
        }

        res = self.client().post('/search', json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertTrue(data['total_questions'])
    
    def test_get_questions_by_category(self):
        category_id = 1
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], category_id)
    
    def test_get_questions_by_category_not_found(self):
        category_id = 100
        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['current_category'], category_id)

    def test_quizzes(self):
        input = {
            "previous_questions": [5,9],
            "quiz_category": {"id": 1, "type": "Science"}
        }
        res = self.client().post('/quizzes', json=input)
        data = json.loads(res.data)
        print(data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], input['quiz_category']['id'])
        self.assertNotEqual(data['question']['id'], input['previous_questions'][0])
        self.assertNotEqual(data['question']['id'], input['previous_questions'][1])
    
    def test_quizzes_not_found(self):
        # get all the question ids
        questions = Question.query.all()
        question_ids = [int(question.id) for question in questions]

        input = {
            "previous_questions": question_ids,
            "quiz_category": {"id": 1, "type": "Science"}
        }
        res = self.client().post('/quizzes', json=input)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], None)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
