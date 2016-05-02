"""Player, Board, and TileBag classes for scrabble game"""

import os
import sys
import logging
import xml.etree.ElementTree as ET
from random import randrange

class Game(object):
    """Parent game class, set the rules"""

    def __init__(self, name='Untitled', max_rack_letters=7, letter_ratio_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'config','letter_ratios_en-us.xml'), board_setup_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),'config','board_config.xml')):
        """Set up the board and tile bag, add the players"""
        self.name = name
        self.logger = logging.getLogger(type(self).__name__)
        self.max_rack_letters = max_rack_letters
        self.players = {}
        self.board = Board(board_setup_file)
        self.tilebag = TileBag(letter_ratio_file)

    def add_players(self,num_players=2,player_names=[],max_players=4):
        if num_players > max_players:
            raise ValueError('Exceeded maximum number of players %d.'%max_players)

        if player_names and len(player_names) != num_players:
            raise ValueError('List of player names must be equal to number of players.')

        for i in range(num_players):
            if not player_names:
                pname='player%d'%(i)
            else:
                pname=player_names[i]
            self.players[pname] = Player(self.tilebag,self.max_rack_letters,name=pname)


class Board(object):
    """Scrabble board class"""

    def __init__(self, board_setup_file, default_color='#BBB89E'):
        """Setup scrabble board"""
        self.logger = logging.getLogger(type(self).__name__)
        self.board_matrix = []
        tree = ET.parse(board_setup_file)
        root = tree.getroot()
        special_spaces = root.find('special')
        dims = root.find('dimensions')
        nrows,ncols = int(dims.attrib['rows']),int(dims.attrib['cols'])
        self.dims = (nrows,ncols)
        for j in range(ncols):
            for i in range(nrows):
                self.board_matrix.append({'label':None, 'wmult':1, 'lmult':1, 'letter':None, 'x':j, 'y':i, 'color':default_color})

        for space in special_spaces:
            i_row,i_col = int(space.attrib['row']),int(space.attrib['col'])
            for square in self.board_matrix:
                if square['x'] == i_col and square['y'] == i_row:
                    square['label'] = space.attrib['label']
                    square['wmult'] = space.attrib['wmult']
                    square['lmult'] = space.attrib['lmult']
                    square['color'] = space.attrib['color']


class TileBag(object):
    """Scrabble TileBag class"""

    def __init__(self,letter_ratio_file):
        """Create the bag of letter tiles with appropriate ratios"""
        self.logger = logging.getLogger(type(self).__name__)
        self.letters = []
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
        i_draw = randrange(0,len(self.letters))
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

    def __init__(self,tilebag,max_rack_letters,name='player'):
        """Create player"""
        self.logger = logging.getLogger(type(self).__name__)
        self.max_rack_letters=max_rack_letters
        self.name=name
        self.score = 0
        self.letter_rack = []
        self.logger.info('Creating letter rack for player %s'%self.name)
        tilebag.draw_letters(self)

    def show_rack(self):
        """Display letter rack"""
        for lr in self.letter_rack:
            print('%s, %d'%(lr['letter'],lr['points']))

    def play_word(self,word='',direction='horizontal',start_pos=(0,0)):
        """Make a word"""
        if direction=='horizontal':
            d=(0,1)
        else:
            d=(1,0)
        word_letters = list(word.upper())
        rack_copy = list(self.letter_rack)
        word_play = []
        for wl,i in zip(word_letters,range(len(word_letters))):
            found_flag=False
            for lr,j in zip(rack_copy,range(len(rack_copy))):
                if wl == lr['letter']:
                    word_play.append({'letter':wl, 'points':lr['points'], 'rpos':start_pos[0] + i*d[0], 'cpos':start_pos[1] + i*d[1]})
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
