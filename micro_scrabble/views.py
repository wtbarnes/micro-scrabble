from flask import Flask,render_template
from micro_scrabble import app
from forms import NewGameForm
import game as scrabble

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',title='Scrabble In a Bottle')

@app.route('/new_game',methods=['GET','POST'])
def new_game():
    """Form for submitting new game"""
    #name,players = None,None
    create_game_form = NewGameForm()
    if create_game_form.validate_on_submit():
        if not create_game_form.name.data:
            name = 'Untitled Game'
        else:
            name = create_game_form.name.data
        players = create_game_form.players.data.split(',')
        game  = scrabble.Game(name=name)
        game.add_players(player_names=players,num_players=len(players))
        cur_game(name)
    return render_template('new_game.html',form=create_game_form)


@app.route('/game-<name>')
def cur_game(name):
    """Current game page"""
    s = 50
    game  = scrabble.Game(name=name)
    return render_template('board.html', name=game.name, height=game.board.dims[0]*s, width=game.board.dims[1]*s, square=s, board_matrix=game.board.board_matrix)


@app.route('/game-<game_name>/players/<player_name>',methods=['GET','POST'])
def player(game,game_name,player_name):
    """Player Page"""


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
