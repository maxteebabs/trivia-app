import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  db = SQLAlchemy(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS(app, resources={r"*api/*": {origins: '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,PUT,DELETE,OPTIONS,PATCH')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=["GET"])
  def get_categories():
    categories = Category.query.all()
    # formatted_categories = [category.format() for category in categories]
    formatted_categories = {}
    for category in categories:
        formatted_categories[category.id] = category.type
    return jsonify({
        "categories": formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=["GET"])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * QUESTIONS_PER_PAGE
    total_questions = Question.query.count()
    questions = Question.query.offset(offset).limit(QUESTIONS_PER_PAGE).all()
    formatted_questions = [question.format() for question in questions]

    # query for categories
    categories = Category.query.all()

    formatted_categories = {}
    for category in categories:
        formatted_categories[category.id] = category.type

    return jsonify({
      'questions': formatted_questions,
      'total_questions': total_questions,
      'categories': formatted_categories,
      'current_category':1
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if not question:
      # do something
      abort(404)
    try:
      status = question.delete()
      return jsonify({
          'success': True
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=["POST"])
  def create_question():
    body = request.get_json()
    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', 0)
    if not question or not answer or not category or not difficulty:
        abort(400)
    try:
      question = Question(question, answer, category, difficulty)
      question.insert()
      return jsonify({
          'success': True,
          'question': question.id,
          'total_questions': Question.query.count()
      })
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(422)
    finally:
      db.session.close()
    

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=["POST"])
  def search_questions():
    body = request.get_json()
    searchTerm = body.get('searchTerm', None)
    questions = Question.query.filter(
        Question.question.ilike(f'%{searchTerm}%')).all()
    formatted_questions = [question.format() for question in questions]
    return jsonify({
        'current_category': 1,
        'questions': formatted_questions,
        'total_questions': Question.query.count()
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=["GET"])
  def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    formatted_questions = [question.format() for question in questions]

    return jsonify({
        'questions': formatted_questions,
        'total_questions': len(formatted_questions),
        'current_category': category_id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=["POST"])
  def quizzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)
    if not quiz_category:
      abort(400)

    
    if not quiz_category or int(quiz_category['id']) == 0:
      # category is not provided
      query = Question.query
    else:
      query = Question.query.filter(Question.category == quiz_category['id'])
    
    questions = query.filter(
      Question.id.notin_(previous_questions)).all()

    # random questions
    if len(questions) > 0:
      random_integer = random.randrange(0, len(questions))
      question = questions[random_integer]
      question = question.format()
    else:
      question = None

    return jsonify({
        'question': question,
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "Not found"
    }), 404
  
  @app.errorhandler(422)
  def unprocessible(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "Unprocessible"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': "Bad Request"
    }), 400
    
  return app

    
