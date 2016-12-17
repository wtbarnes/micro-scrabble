"""Player, Board, and TileBag classes for scrabble game"""

import os
import sys
import logging
import xml.etree.ElementTree as ET
import random

from models import GameArchive


class Game(object):
    """Parent game class, set the rules"""

    def __init__(self, name='Untitled', max_rack_letters=7, letter_ratio_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'config','letter_ratios_en-us.xml'), board_setup_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'config','board_config.xml'),board_matrix=[],dims=[],letters=[]):
        """Set up the board and tile bag, add the players"""
        self.name = name
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug('Configuring game with name %s'%self.name)
        self.max_rack_letters = max_rack_letters
        self.players = {}
        self.board = Board(board_setup_file=board_setup_file, board_matrix=board_matrix, dims=dims)
        self.tilebag = TileBag(letter_ratio_file,letters)

    def add_players(self, num_players=2, player_names=[], max_players=4, scores=[], letter_racks=[],player_order=[]):
        if num_players > max_players:
            raise ValueError('Exceeded maximum number of players %d.'%max_players)
        if player_names and len(player_names) != num_players:
            raise ValueError('List of player names must be equal to number of players.')
        for i in range(num_players):
            if not player_names:
                pname='player%d'%(i)
            else:
                pname=player_names[i]
            if not scores:
                score = 0
            else:
                score = scores[pname]
            if not letter_racks:
                letter_rack = []
            else:
                letter_rack = letter_racks[pname]
            self.players[pname] = Player(self.tilebag, self.max_rack_letters,
                                        name=pname, letter_rack=letter_rack, score=score)

        if not player_order:
            self.player_order = [s[0] for s in sorted([(pname,random.random()) \
                                    for pname in self.players],key=lambda x:x[1])]
        else:
            self.player_order = player_order

    def archive(self,db,archive=None):
        """
        Put class instance into a SQL table
        """
        player_list,letter_racks,scores = [],{},{}
        for key in self.players:
            player_list.append(key)
            letter_racks[key] = self.players[key].letter_rack
            scores[key] = self.players[key].score

        #if a database and entry have been passed, update database
        if archive:
            archive.update({'board_matrix':self.board.board_matrix,
            'letters':self.tilebag.letters,'letter_racks':letter_racks,
            'scores':scores,'player_order':self.player_order})
        else:
            archive = GameArchive(self.name, self.board.board_matrix,
                                    self.tilebag.letters, self.board.dims,
                                    self.max_rack_letters, player_list, scores,
                                    letter_racks, self.player_order)
            db.session.add(archive)
        db.session.commit()

    @classmethod
    def unarchive(cls,archive):
        """
        Restore game state from SQL entry
        """
        game = cls(name=archive.first().game_name,
                            max_rack_letters=archive.first().max_rack_letters,
                            letter_ratio_file='', board_setup_file='',
                            board_matrix = archive.first().board_matrix,
                            dims=archive.first().dims, letters=archive.first().letters)
        game.add_players(num_players=len(archive.first().players),
                        player_names=archive.first().players,
                        scores=archive.first().scores,
                        letter_racks=archive.first().letter_racks,
                        player_order=archive.first().player_order)
        return game

    def score_word(self,word_coords,player_name):
        """
        Calculate score of a play and increment player score
        """
        score,wmult = 0,1
        #sum points of played word
        for wc in word_coords:
            score += self.board.board_matrix[wc]['points']\
                    *self.board.board_matrix[wc]['lmult']
            wmult *= self.board.board_matrix[wc]['wmult']

        score *= wmult
        #TODO:traverse the board and add the score appropriately (hard...)
        #FIXME:really need to walk the board until we find an empty letter since the played words do not have all of the letters in them that the scoring word does
        #add score to player

        self.players[player_name].score += score


class Board(object):
    """Scrabble board class"""

    def __init__(self, board_matrix=[],board_setup_file='',dims=[]):
        """Setup scrabble board"""
        self.logger = logging.getLogger(type(self).__name__)
        if board_setup_file:
            self.logger.debug('Configuring board from setup file %s'%(board_setup_file))
            self._setup_board(board_setup_file)
        elif dims and board_matrix:
            self.board_matrix = board_matrix
            self.dims = dims
        else:
            self.logger.error('Specify config file or preexisting board setup.')

    def _setup_board(self,board_setup_file,default_color='#BBB89E'):
        """Configure board"""
        self.logger.debug('Setting up board')
        tree = ET.parse(board_setup_file)
        root = tree.getroot()
        special_spaces = root.find('special')
        dims = root.find('dimensions')
        nrows,ncols = int(dims.attrib['rows']),int(dims.attrib['cols'])
        self.dims = [nrows,ncols]
        self.board_matrix = []
        self.logger.debug('Setting board dimensions to (%d,%d)'%(self.dims[0],self.dims[1]))
        for j in range(ncols):
            for i in range(nrows):
                self.board_matrix.append({'label':None, 'wmult':1, 'lmult':1, 'letter':None, 'x':j, 'y':i, 'color':default_color, 'points':0})
        for space in special_spaces:
            i_row,i_col = int(space.attrib['row']),int(space.attrib['col'])
            for square in self.board_matrix:
                if square['x'] == i_col and square['y'] == i_row:
                    square['label'] = space.attrib['label']
                    square['wmult'] = int(space.attrib['wmult'])
                    square['lmult'] = int(space.attrib['lmult'])
                    square['color'] = space.attrib['color']

    def place_tiles(self,tiles,tile_color='#E1BF9A'):
        """Put tiles from play on board"""
        coords = []
        for t in tiles:
            for i in range(len(self.board_matrix)):
                if t['rpos'] == self.board_matrix[i]['y'] and t['cpos'] == self.board_matrix[i]['x']:
                    self.board_matrix[i]['letter'] = t['letter']
                    self.board_matrix[i]['points'] = t['points']
                    self.board_matrix[i]['color'] = tile_color
                    coords.append(i)
                    break

        return coords


class TileBag(object):
    """Scrabble TileBag class"""

    def __init__(self,letter_ratio_file='',letters=[]):
        """Create the bag of letter tiles with appropriate ratios"""
        if not letter_ratio_file and not letters:
            raise ValueError('Specify existing letter bag or config file.')

        self.logger = logging.getLogger(type(self).__name__)
        self.letters = letters
        if not self.letters:
            self._make_bag(letter_ratio_file)

    def _make_bag(self,letter_ratio_file):
        """Construct tilebag"""
        tree = ET.parse(letter_ratio_file)
        root = tree.getroot()
        for child in root:
            self.letters.extend(int(child.attrib['number'])*[{'letter':child.attrib['char'], 'points':int(child.attrib['points'])}])

    def draw_letters(self,player):
        """Draw multiple letters from bag"""
        num_letters_needed = player.max_rack_letters - len(player.letter_rack)
        for _ in range(num_letters_needed):
            if len(self.letters) > 0:
                self._draw_letter(player)
            else:
                print('Tile bag is empty. No. of letters = %d'%len(self.letters))
                break

    def swap_letter(self,player,letter):
        """Swap a letter from the players rack with one in the bag"""
        letter_rack_letters = [r['letter'] for r in player.letter_rack]
        try:
            i_swap = letter_rack_letters.index(letter.upper())
            self.letters.append(player.letter_rack[i_swap])
            player.letter_rack.pop(i_swap)
            self._draw_letter(player)
        except ValueError:
            print('Cannot swap %s. Not in letter rack.'%letter)

    def _draw_letter(self,player):
        """Draw a letter from the bag, add it to the rack of a player instance"""
        i_draw = random.randrange(0,len(self.letters))
        player.letter_rack.append(self.letters[i_draw])
        self.letters.pop(i_draw)

    def display_letter_count(self):
        """Display how many letters are left in the bag"""
        print('Number of letters left in tile bag: %d'%(len(self.letters)))

    def _display_bag(self):
        """Show the contents of the tile bag. Should not be used in game"""
        print(self.letters)


class Player(object):
    """Class to control player action and movement"""

    def __init__(self,tilebag,max_rack_letters,name='player',letter_rack=[],score=0):
        """Create player"""
        self.logger = logging.getLogger(type(self).__name__)
        self.max_rack_letters=max_rack_letters
        self.name=name
        self.score = score
        self.letter_rack = letter_rack
        tilebag.draw_letters(self)

    def show_rack(self):
        """Display letter rack"""
        for lr in self.letter_rack:
            print('%s, %d'%(lr['letter'],lr['points']))

    def play_word(self,word='',tile_pos=[]):
        """Make a word"""
        word_letters = list(word.upper())
        rack_copy = list(self.letter_rack)
        word_play = []
        for i,wl in enumerate(word_letters):
            found_flag=False
            for j,lr in enumerate(rack_copy):
                if wl == lr['letter']:
                    word_play.append({'letter':wl, 'points':lr['points'],
                                    'rpos':tile_pos[i][0], 'cpos':tile_pos[i][1]})
                    found_flag=True
                    rack_copy.pop(j)
                    break
            if not found_flag:
                print('Letter %s not in letter rack. Try another word.'%wl)
                word_play = []
                break

        if found_flag:
            self.letter_rack = rack_copy

        return word_play
