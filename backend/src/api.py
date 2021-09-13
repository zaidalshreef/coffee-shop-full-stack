import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES



#get drinks from database
@app.route('/drinks', methods=['GET'])
def drinks():
    
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })





# get drinks detail from database
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })





# create new drink and add it to database
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(payload):
    
    req = request.get_json()
    try:
        # create new drink
        drink = Drink()
        drink.title = req['title']
        drink.recipe = json.dumps(req['recipe'])
        # add new drink to database
        drink.insert()
        
     # abort if error occurred when create new drink   
    except :
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
        })





# Edit drink by givin id from database
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_by_id(payload, id):
    
    req = request.get_json()
    
    # get drink from  database by givin id
    drink = Drink.query.get(id)

   # if there is no drink by the givin id abort
    if (drink is None):
      abort(422)

    try:
        title = req.get('title')
        recipe = req.get('recipe')
        #check if title updated
        if title is not None:
           drink.title = title
        #check if recipe updated
        if recipe is not None:
           drink.recipe = json.dumps(req['recipe'])

       # update drink in database
        drink.update()
        
    # abort if update is not successful    
    except :
        abort(422)

    return jsonify({'success': True, 'drinks': [drink.long()]})







# delete drink from database by givin id
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # get drink from  database by givin id
    drink = Drink.query.get(id)
  # if there is no drink by the givin id
    if drink is None:
        abort(404)

    try:
        # delete drink
        drink.delete()
    
    # abort if there problem delete drink    
    except :
        abort(400)

    return jsonify({'success': True, 'delete': id})


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

@app.errorhandler(403)
def access_forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "you do not have permission to access this resource"
    }), 403

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'unauthenticated'
    }), 401



@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'The server could not understand the request due to invalid syntax.'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405