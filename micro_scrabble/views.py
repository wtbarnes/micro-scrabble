from flask import Flask,render_template
from micro_scrabble import app
import game as scrabble

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',title='Scrabble In a Bottle')

@app.route('/board')
def render_board():
    s = 50
    game = scrabble.Game()
    game.board.board_matrix[34]['letter'] = 'F'
    game.board.board_matrix[35]['letter'] = 'O'
    game.board.board_matrix[36]['letter'] = 'O'
    game.board.board_matrix[49]['letter'] = 'A'
    game.board.board_matrix[64]['letter'] = 'L'
    game.board.board_matrix[79]['letter'] = 'S'
    game.board.board_matrix[94]['letter'] = 'E'

    return render_template('board.html', height=game.board.dims[0]*s, width=game.board.dims[1]*s, square=s, board_matrix=game.board.board_matrix)
