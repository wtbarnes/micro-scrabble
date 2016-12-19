"""Player object"""

import os
import sys
import logging

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
