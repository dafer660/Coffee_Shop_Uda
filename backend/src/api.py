import os
from flask import Flask, request, jsonify, abort, make_response
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
cors = CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''


db_drop_and_create_all()


def drinkify(drinks, representation=''):
    if representation == 'long':
        return [drink.long() for drink in drinks]
    return [drink.short() for drink in drinks]


# ROUTES

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,PATCH')
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    return response


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.title).all()
        result = drinkify(drinks, representation='long')

        if len(drinks) == 0:
            abort(404)

        return make_response(
            jsonify({
                'success': True,
                'drinks': result
            }), 200
        )

    except AuthError:
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = Drink.query.order_by(Drink.title).all()
        result = drinkify(drinks, representation='long')

        if len(drinks) == 0:
            abort(404)

        return make_response(
            jsonify({
                'success': True,
                'drinks': result
            }), 200
        )

    except AuthError:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        req = request.get_json()
        new_drink = Drink(
            title=req['title'],
            recipe=json.dumps(req['recipe'])
        )
        new_drink.insert()

        return make_response(
            jsonify({
                'success': True,
                'drinks': new_drink.long()
            }), 200
        )

    except AuthError:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    try:
        req = request.get_json()
        title = req.get('title', None)
        recipe = req.get('recipe', None)
        drink = Drink.query.filter_by(id=id).first()

        if drink is None:
            abort(404)

        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()

        return make_response(
            jsonify({
                'success': True,
                'drinks': [drink.long()]
            }), 200
        )

    except AuthError:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter_by(id=id).first()

        if drink is None:
            abort(404)

        drink.delete()

        return make_response(
            jsonify({
                'success': True,
                'delete': id
            }), 200
        )

    except AuthError:
        abort(422)


# Error Handling


@app.errorhandler(400)
def bad_reques(error):
    return jsonify({
        'message': error.description,
        'error': 400,
        'success': False
    }), 400


@app.errorhandler(401)
def not_found(error):
    return jsonify({
        'message': error.description,
        'error': 401,
        'success': False
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'message': error.description,
        'error': 404,
        'success': False
    }), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        'message': error.description,
        'error': 405,
        'success': False
    }), 405


@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        'message': error.description,
        'error': 422,
        'success': False
    }), 422


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'message': error.description,
        'error': 500,
        'success': False
    }), 500


@app.errorhandler(AuthError)
def auth_error(err):
    return jsonify({
        'message': err.error['description'],
        'error': err.status_code,
        'success': False
    }), err.status_code
