from flask import Flask,render_template

from forms import NewGameForm,PlayerForm,SwapLettersForm
from models import GameArchive
from micro_scrabble import app,db
from micro_scrabble.game import Game

#board config
s = 50

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
        #split the string of player names
        #TODO: error handling if this is not formatted correctly
        players = create_game_form.players.data.split(',')
        #Instantiate class
        game  = Game(name=create_game_form.name.data)
        #add players
        game.add_players(player_names=players,num_players=len(players))
        #add to database
        game.archive(db)

    return render_template('new_game.html',form=create_game_form)

@app.route('/current_games')
def show_games():
    """List all current games"""
    all_games = GameArchive.query.all()
    return render_template('current_games.html',games=all_games)

@app.route('/delete-game-<game_name>')
def delete_game(game_name):
    """Delete game from database"""
    game_archive = GameArchive.query.filter_by(game_name=game_name).first()
    db.session.delete(game_archive)
    db.session.commit()
    all_games = GameArchive.query.all()
    return render_template('current_games.html',games=all_games)

@app.route('/game-<game_name>')
def cur_game(game_name):
    """Current game page"""
    #rebuild class instance from query
    game  = Game.unarchive(GameArchive.query.filter_by(game_name=game_name))
    #first render the JS
    d3_board = render_template('js/board.js',height=game.board.dims[0]*s,
                                width=game.board.dims[1]*s, square=s,
                                board_matrix=game.board.board_matrix)
    return render_template('board.html',name=game.name,d3_board=d3_board,
        player_list=[{'name':game.players[key].name,
                    'score':game.players[key].score,
                    'your_turn':game.players[key].name==game.player_order[0]} \
                                            for key in game.players])

@app.route('/game-<game_name>/players/<player_name>',methods=['GET','POST'])
def player_view(game_name,player_name):
    """Player Page"""
    #rebuild class instance from SQL request
    game_archive = GameArchive.query.filter_by(game_name=game_name)
    game = Game.unarchive(game_archive)
    #make forms
    player_form = PlayerForm()
    swap_form = SwapLettersForm()
    #validation for play submission
    if player_name != game.player_order[0]:
        pass
    elif player_form.validate_on_submit():
        #parse tile positions
        tile_pos = [(int(r),int(c)) for r,c in zip(player_form.rows.data.split(','), player_form.cols.data.split(','))]
        #play word
        played_word = game.players[player_name].play_word(word=player_form.word_play.data,  tile_pos=tile_pos)
        #place tiles
        coords = game.board.place_tiles(played_word)
        #score word
        game.score_word(coords,player_name)
        #draw letters
        game.tilebag.draw_letters(game.players[player_name])
        #increment turn list
        game.player_order.append(game.player_order.pop(0))
        #update database
        game.archive(db,archive=game_archive)
    elif swap_form.validate_on_submit():
        #swap_letter
        game.tilebag.swap_letter(game.players[player_name],swap_form.letter.data)
        #increment turn list
        game.player_order.append(game.player_order.pop(0))
        #update database
        game.archive(db,archive=game_archive)

    #first render the JS
    d3_rack = render_template('js/player.js',square=2*s,
                                letter_rack=game.players[player_name].letter_rack,
                                num_letters=len(game.players[player_name].letter_rack))
    return render_template('player.html',submit_form=player_form,swap_form=swap_form,
                            name=player_name,your_turn=player_name==game.player_order[0],
                            d3_rack=d3_rack)
