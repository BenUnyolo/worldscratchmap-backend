from flask import request, jsonify, current_app
from functools import wraps
from extensions import mysql
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            # TODO move next 2 bits out?
            try:
                cur = mysql.connection.cursor()
            except Exception as err:
                print(err)
                return jsonify({'message': 'Issue connecting to database'}), 500
            cur.execute('''SELECT * FROM users
                WHERE user_id = %s''', [data['user_id']])
            current_user = cur.fetchone()
            cur.close()

        except Exception as err:
            print(err)
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
