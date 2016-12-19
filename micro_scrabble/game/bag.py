"""Letter bag object"""

import logging
import random
import xml.etree.ElementTree as ET


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
