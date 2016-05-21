from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, RadioField, IntegerField
from wtforms.validators import Required

class NewGameForm(Form):
    """Form for submitting new game"""
    name = StringField('Game name:',default='Untitled')
    players = StringField('Players (comma delimited):',validators=[Required()])
    submit = SubmitField('Create Game')

class PlayerForm(Form):
    """Show player rack and options"""
    word_play = StringField('Word to play:',validators=[Required()])
    rows = StringField('Row positions (comma delimited):',validators=[Required()])
    cols = StringField('Column positions (comma delimited):',validators=[Required()])
    submit = SubmitField('Play!')

class SwapLettersForm(Form):
    """Click to draw new letters"""
    letter = StringField('Letter to Swap')
    submit = SubmitField('Swap Letter')
