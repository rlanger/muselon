import os
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from config import basedir

muselon = Flask(__name__)
muselon.config.from_object('config')
db = SQLAlchemy(muselon)
lm = LoginManager()
lm.init_app(muselon)
lm.login_view = 'login'

from muselon import views, models
