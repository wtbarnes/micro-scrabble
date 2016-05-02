import os,sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from flask import Flask
from flask_bootstrap import Bootstrap

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    return app

app = create_app()
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'
#app.config.from_object('flask_config')

from micro_scrabble import views
