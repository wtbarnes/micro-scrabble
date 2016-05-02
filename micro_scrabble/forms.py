from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NewGameForm(Form):
    name = StringField('Game name:')
    players = StringField('Players (comma delimited):',validators=[Required()])
    submit = SubmitField('Create Game')
