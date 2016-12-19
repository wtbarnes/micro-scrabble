"""Board object"""

import os
import sys
import logging
import xml.etree.ElementTree as ET
import random

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
