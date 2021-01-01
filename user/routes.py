from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import re
import jwt
import datetime
from helpers import *
from extensions import mysql

user = Blueprint('user', '__name__', url_prefix='/user')

@user.route('/', methods=['GET'])
@token_required
def get_user(current_user):
    # TODO not sure about error code ont this one
    if not current_user:
        return jsonify({'message': "Cannot perform that function!"}), 401

    user = {
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "user_id": current_user["user_id"],
        "username": current_user["username"]
    }

    return jsonify(user)


@user.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Missing field(s)'}), 401

    # create db
    try:
        cur = mysql.connection.cursor()
    except Exception as err:
        return jsonify({'message': 'Issue connecting with database'}), 500

    # search db for user
    cur.execute('''SELECT * FROM users
        WHERE username = %s''', [auth.username])
    user = cur.fetchone()

    if not user:
        return jsonify({'message': "Couldn't find a user with that username"}), 401

    # check if password is correct, if so create token
    if check_password_hash(user['pass'], auth.password):
        token = jwt.encode({'user_id': user['user_id'], 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=120)}, current_app.config['SECRET_KEY'])

        userRes = {
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "user_id": user["user_id"],
            "username": user["username"]
        }

        # # TODO why are we decoding here?
        # return jsonify({'token': token.decode('UTF-8'), 'user': userRes}), 200
        return jsonify({'token': token, 'user': userRes}), 200

    return jsonify({'message': "Couldn't verify credentials"}), 401


@user.route('/', methods=['POST'])
def create_user():
    data = request.get_json()

    # username validation
    if not data['username']:
        return jsonify({'message': "No username"}), 400
    if len(data['username']) < 3 or len(data['username']) > 20:
        return jsonify({'message': "Username must be between 3 and 20 characters"}), 400

    # first name validation
    if not data['first_name']:
        return jsonify({'message': "No first name"}), 400
    if len(data['first_name']) > 30:
        return jsonify({'message': "First name must be less than 30 characters"}), 400

    # last name validation
    if data['last_name'] and (len(data['last_name']) > 30):
        return jsonify({'message': "Last name must be less than 30 characters"}), 400

    # email validation
    if not data['email']:
        return jsonify({'message': "No email"}), 400
    if len(data['email']) > 320:
        return jsonify({'message': "Email address too long"}), 400
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", data['email']):
        return jsonify({'message': "Invalid email address"}), 400

    # password validation
    if not data['password_verify'] or not (data['password'] == data['password_verify']):
        return jsonify({'message': "Two entered passwords do not match"}), 400
    if not data['password']:
        return jsonify({'message': "No password"}), 400
    if len(data['password']) < 8:
        return jsonify({'message': "Password must be at least 8 characters"}), 400
    if len(data['password']) > 100:
        return jsonify({'message': "Password must be less than 100 characters"}), 400

    try:
        cur = mysql.connection.cursor()
    except Exception as err:
        return jsonify({'message': "Issue connecting with database"}), 500

    # check if username exists
    cur.execute('''SELECT * FROM users
        WHERE username = %s''', [data['username']])
    check_user = cur.fetchall()
    if check_user:
        cur.close()
        return jsonify({'message': "This username is taken, please choose another"}), 400

    # check if email exists
    cur.execute('''SELECT * FROM users
        WHERE email = %s''', [data['email']])
    check_email = cur.fetchall()
    if check_email:
        cur.close()
        return jsonify({'message': "email exists"}), 400

    # hash password
    hashed_password = generate_password_hash(data['password'], method='sha256')

    user = {
        "username": data['username'],
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "password": hashed_password
    }

    # create query to add user to db
    query = '''INSERT INTO users (username, first_name, last_name, email, pass)
         VALUES (%(username)s, %(first_name)s, %(last_name)s, %(email)s, %(password)s)'''

    # TODO sort out except statement
    try:
        cur.execute(query, user)
        mysql.connection.commit()
        cur.close()
    except Exception as err:
        return jsonify({'message': 'There was a server error when trying to create your user account, try again later or let us know'}), 500

    return jsonify({'message': 'New user created!'}), 200

# TODO make this route
@user.route('/<user_id>', methods=['PUT'])
def edit_email(user_id):
    # find the user

    # if not ..

    # change email

    return ''


@user.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):

    # same as edit email but with delete instead of change

    return ''