"""Main game object"""

import os
import sys
import logging
import random

from micro_scrabble.models import GameArchive
from micro_scrabble.game import Player,Board,TileBag

class Game(object):
    """Parent game class, set the rules"""

    def __init__(self, name='Untitled', max_rack_letters=7, letter_ratio_file=None,
                board_setup_file=None,board_matrix=[],dims=[],letters=[]):
        """Set up the board and tile bag, add the players"""
        self.name = name
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug('Configuring game with name %s'%self.name)
        self.max_rack_letters = max_rack_letters
        self.players = {}
        #setup board
        if board_setup_file is None:
            board_setup_file=os.path.join(os.path.dirname(
                                          os.path.dirname(
                                          os.path.realpath(__file__))),
                                          'config','board_config.xml')
        self.board = Board(board_setup_file=board_setup_file, board_matrix=board_matrix, dims=dims)
        #setup tilebag
        if letter_ratio_file is None:
            letter_ratio_file=os.path.join(os.path.dirname(
                                           os.path.dirname(
                                           os.path.realpath(__file__))),
                                           'config','letter_ratios_en-us.xml')
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
        #TODO:traverse the board and add the score appropriately (hard...)
        #FIXME:really need to walk the board until we find an empty letter since the played words do not have all of the letters in them that the scoring word does
        #add score to player

        # TODO: how do you find direction when there's only one tile?
        direction = (self.board.board_matrix[word_coords[1]]['x']\
                     -self.board.board_matrix[word_coords[0]]['x'],
                     self.board.board_matrix[word_coords[1]]['y']\
                     -self.board.board_matrix[word_coords[0]]['y'])
        # find the leftmost (or bottommost) coordinate
        word_end = False
        current_coords = (self.board.board_matrix[word_coords[0]]['x'],
                          self.board.board_matrix[word_coords[0]]['y'])
        while not word_end:
            new_coords = (current_coords[0]-direction[0],
                          current_coords[1]-direction[1])
            try:
                tile = (t for t in self.board.board_matrix\
                        if t['x']==new_coords[0] and t['y']==new_coords[1]).next()
                if tile['label'] is None:
                    start_coords = current_coords
                    word_end = True
                else:
                    current_coords = new_coords
            except StopIteration:
                start_coords = current_coords
                word_end = True

        print('starting coordinates are')
        print(start_coords)

        # traverse the word and sum the score
        score,wmult_total = 0,1
        word_end = False
        while not word_end:
            try:
                tile = (t for t in self.board.board_matrix\
                        if t['x']==start_coords[0] and t['y']==start_coords[1]).next()
                if tile['label'] is None:
                    word_end = True
                else:
                    # only use multipliers from this turn
                    if self.board.board_matrix.index(tile) in word_coords:
                        score += tile['points']*tile['lmult']
                        wmult_total *= tile['wmult']
                    else:
                        score += tile['points']
                    start_coords = (start_coords[0]+direction[0],
                                    start_coords[1]+direction[1])
            except StopIteration:
                word_end = True

        # apply total word multipliers
        score *= wmult_total

        self.players[player_name].score += score
