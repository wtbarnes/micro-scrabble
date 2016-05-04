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
    start_row = IntegerField('Row to put the first tile:',validators=[Required()])
    start_col = IntegerField('Column to put the first tile:',validators=[Required()])
    direction = RadioField('Direction of word', validators=[Required()], choices=[('horizontal','Horizontal'),('vertical','Vertical')], default='hor')
    submit = SubmitField('Play!')

class DrawLettersForm(Form):
    """Click to draw new letters"""
    submit = SubmitField('Draw Letters')
