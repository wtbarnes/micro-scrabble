import os,sys
import logging
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    return app

logging.basicConfig(level=logging.DEBUG)
app = create_app()
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +  os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'db','micro_scrabble.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
#app.config.from_object('flask_config')

from micro_scrabble import views
