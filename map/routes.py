from flask import Blueprint, request, jsonify
from helpers import *
from extensions import mysql

map = Blueprint('map', '__name__', url_prefix='/map')

@map.route('/', methods=['POST'])
@token_required
def add_countries(current_user):
    data = request.get_json()

    # set up list for duplicate check
    countries_array = []
    for item in data:
        countries_array.append(item["country"])
    # check for duplicate countries
    if len(set(countries_array)) != len(countries_array):
        jsonify({"Duplicate country found, remove duplicate and try again"}), 400

    try:
        cur = mysql.connection.cursor()
    except Exception as err:
        return jsonify({"Issue connecting with database, please try again"}), 500

    # lists to keep track of which countries can be added, and which are duplicated
    to_push = []
    duplicates = []
    # variable to help keep track of if we were able to succesfully add countries
    write_success = False
    # check if already added
    for item in data:
        cur.execute('''SELECT * FROM visited
            WHERE user_id = %s AND country_code = %s''', [current_user['user_id'], item["country"]])
        check_duplicate = cur.fetchall()
        if check_duplicate:
            duplicates.append(item["country"])
        else:
            to_push.append(
                [current_user['user_id'], item["country"], item["year"]])

    if (len(to_push) > 0):
        # create query to add user to db
        query = '''INSERT INTO visited (user_id, country_code, year_visited)
            VALUES (%s, %s, %s)'''

        # TODO sort out except statement
        try:
            cur.executemany(query, to_push)
            mysql.connection.commit()
            write_success = True
            cur.close()
        except Exception as err:
            # TODO write a message e.g. there was an error form our server:
            return (str(err))

    response = {
        "write_success": write_success,
        "duplicates": duplicates
    }

    return jsonify(response)


@map.route('/<user_id>', methods=['GET'])
def get_countries(user_id):
    try:
        cur = mysql.connection.cursor()
    except Exception as err:
        return jsonify({"message": "Issue connecting with database"}), 500

    # check if user exists
    user_id = int(user_id)
    # search db for that user
    cur.execute('''SELECT * FROM users
        WHERE user_id = %s''', [user_id])
    user = cur.fetchall()

    if not user:
        return jsonify({'message': 'No user found with that ID'}), 404

    # fetch countries
    cur.execute('''SELECT visited.country_code, countries.country, visited.year_visited
        FROM visited
        JOIN countries ON visited.country_code = countries.country_code
        WHERE user_id = %s''', [user_id])
    countries = cur.fetchall()
    cur.close()

    return jsonify(countries)


@map.route('/<country>', methods=['DELETE'])
@token_required
def delete_country(current_user, country):
    print(country)
    # TODO figure out why this code doesn't throw exception when random stuff passed in (object)
    try:
        cur = mysql.connection.cursor()
    except Exception as err:
        return jsonify({'message': "Database issue"}), 500

    try:
        cur.execute('''DELETE FROM visited
            WHERE user_id = %s AND country_code = %s''', [current_user['user_id'], country])
        mysql.connection.commit()
    except Exception as err:
        return jsonify({'message': "Looks like it's already deleted"}), 400

    return jsonify("Country deleted")