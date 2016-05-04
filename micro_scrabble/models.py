from micro_scrabble import db

class GameArchive(db.Model):
    """SQL model for storing game state"""
    id = db.Column(db.Integer,primary_key=True)
    game_name = db.Column(db.String(200))#,unique=True)
    board_matrix = db.Column(db.PickleType)#,unique=True)
    letters = db.Column(db.PickleType)#,unique=True)
    dims = db.Column(db.PickleType)#,unique=True)
    max_rack_letters = db.Column(db.Integer)#,unique=True)
    players = db.Column(db.PickleType)#,unique=True)
    scores = db.Column(db.PickleType)#,unique=True)
    letter_racks = db.Column(db.PickleType)#,unique=True)

    def __init__(self, game_name, board_matrix, letters, dims, max_rack_letters, players, scores, letter_racks):
        """Build SQL Table"""
        self.game_name = game_name
        self.board_matrix = board_matrix
        self.letters = letters
        self.dims = dims
        self.max_rack_letters = max_rack_letters
        self.players = players
        self.scores = scores
        self.letter_racks = letter_racks

    def __repr__(self):
        return '<Name %r>'%self.game_name
