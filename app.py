from flask import Flask
import os

from extensions import mysql
from helpers import *
from user.routes import user
from map.routes import map

app = Flask(__name__)

app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

app.register_blueprint(user)
app.register_blueprint(map)


if __name__ == '__main__':
    app.run(debug=True)
