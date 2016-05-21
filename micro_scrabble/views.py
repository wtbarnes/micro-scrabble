from flask import Flask,render_template
from micro_scrabble import app
from micro_scrabble import db
from forms import NewGameForm,PlayerForm,SwapLettersForm
from models import GameArchive
import game as scrabble

#board config
s = 50

def update_game(instance,archive):
    """Update SQL table"""
    player_list,letter_racks,scores = [],{},{}
    for key in instance.players:
        player_list.append(key)
        letter_racks[key] = instance.players[key].letter_rack
        scores[key] = instance.players[key].score
    archive.update({'board_matrix':instance.board.board_matrix,
    'letters':instance.tilebag.letters,
    'letter_racks':letter_racks,
    'scores':scores})
    db.session.commit()


def pack_game(instance):
    """Put class instance into a SQL table"""
    player_list,letter_racks,scores = [],{},{}
    for key in instance.players:
        player_list.append(key)
        letter_racks[key] = instance.players[key].letter_rack
        scores[key] = instance.players[key].score
    return GameArchive(instance.name, instance.board.board_matrix, instance.tilebag.letters, instance.board.dims, instance.max_rack_letters, player_list, scores, letter_racks)

def unpack_game(archive):
    """Extract class instance from a SQL table"""
    instance = scrabble.Game(name=archive.first().game_name, max_rack_letters=archive.first().max_rack_letters, letter_ratio_file='', board_setup_file='', board_matrix = archive.first().board_matrix, dims=archive.first().dims, letters=archive.first().letters)
    instance.add_players(num_players=len(archive.first().players), player_names=archive.first().players, scores=archive.first().scores, letter_racks=archive.first().letter_racks)
    return instance

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
        game  = scrabble.Game(name=create_game_form.name.data)
        #add players
        game.add_players(player_names=players,num_players=len(players))
        #add to database
        game_archive = pack_game(game)
        db.session.add(game_archive)
        db.session.commit()
        cur_game(game.name)
        #create player pages
        for p in players:
            player_view(game.name,p)

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
    #make SQL request
    game_archive = GameArchive.query.filter_by(game_name=game_name)
    #rebuild class instance
    game  = unpack_game(game_archive)
    return render_template('board.html', name=game.name, height=game.board.dims[0]*s, width=game.board.dims[1]*s, square=s, board_matrix=game.board.board_matrix, player_list = [{'name':game.players[key].name,'score':game.players[key].score} for key in game.players])


@app.route('/game-<game_name>/players/<player_name>',methods=['GET','POST'])
def player_view(game_name,player_name):
    """Player Page"""
    #make SQL request
    game_archive = GameArchive.query.filter_by(game_name=game_name)
    #rebuild class instance
    game = unpack_game(game_archive)
    #make submit form
    player_form = PlayerForm()
    #make swap letter form
    swap_form = SwapLettersForm()
    #validation for play submission
    if player_form.validate_on_submit():
        #parse tile positions
        tile_pos = [(int(r),int(c)) for r,c in zip(player_form.rows.data.split(','), player_form.cols.data.split(','))]
        #play word
        played_word = game.players[player_name].play_word(word=player_form.word_play.data,  tile_pos=tile_pos)
        #place tiles
        game.board.place_tiles(played_word)
        #draw letters
        game.tilebag.draw_letters(game.players[player_name])
        #update database
        update_game(game,game_archive)
    elif swap_form.validate_on_submit():
        #swap_letter
        game.tilebag.swap_letter(game.players[player_name],swap_form.letter.data)
        #update database
        update_game(game,game_archive)

    return render_template('player.html', submit_form=player_form, swap_form=swap_form, letter_rack=game.players[player_name].letter_rack, num_letters=len(game.players[player_name].letter_rack), name=player_name, square=2*s)
