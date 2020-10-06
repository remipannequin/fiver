#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The main game logic for the five-or-more game
"""

import sys
from random import Random, randrange
from enum import Enum
import math

from board import Board, Direction

__author__="Rémi Pannequin"
__copyright__ = "Copyright 2020"
__credits__ = ["Rémi Pannequin"]
__license__ = "GPL"
__maintainer__ = "Rémi Pannequin"
__email__ = "remi.pannequin@gmail.com"
__status__ = "Development"




class BoardSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


class StatusMessage(Enum):
    DESCRIPTION = 1
    NO_PATH = 2
    GAME_OVER = 3
    NONE = 4


class Mode:
    NORMAL = "normal"
    DISTANCE = "distance"


class NextPiecesGenerator:
    """Pieces and random pieces generator
    """

    def __init__(self, rng, n_next_pieces, n_types):
        """Create a new pieces generator.
        
        >>> g = NextPiecesGenerator(3,5)
        >>> g.pieces
        []
        >>> g.n_next_pieces
        3
        >>> g.n_types
        5
        
        """
        self.rng = rng
        self.pieces = list()
        self.n_next_pieces = n_next_pieces
        self.n_types = n_types


    def yield_next_piece (self):
        return self.rng.randrange (self.n_types)


    def yield_next_pieces (self):
        """add n_next_pieces to the queue
        
        >>> g = NextPiecesGenerator(3,5)
        >>> l = g.yield_next_pieces()
        >>> len(g.pieces)
        3
        >>> l[0] == g.pieces[0] and l[1] == g.pieces[1] and l[2] == g.pieces[2]
        True
        >>> [p >= 0 and p < 5 for p in g.pieces]
        [True, True, True]
        """
        self.pieces.clear ()
        for i in range(self.n_next_pieces):
            id = self.yield_next_piece ()
            self.pieces.append(id)
        return self.pieces



class Game:

    N_TYPES = 7
    N_MATCH = 5

    DIFFICULTY = {BoardSize.SMALL: ( 7, 7, 5, 3 ),
                  BoardSize.MEDIUM: ( 9, 9, 7, 3 ),
                  BoardSize.LARGE: ( 20, 15, 7, 7 ) }

    def __init__(self, size = BoardSize.SMALL, mode = Mode.NORMAL, seed=None):
        """Create new instance of a five-or-more game.
        >>> g = Game(BoardSize.SMALL)
        """
        self.mode = mode
        self.n_rows = Game.DIFFICULTY[size][0]
        self.n_cols = Game.DIFFICULTY[size][1]
        self.n_types = Game.DIFFICULTY[size][2]
        self.n_next_pieces = Game.DIFFICULTY[size][3]
        if seed:
            self.seed = seed
        else:
            self.seed = randrange(sys.maxsize)
        self.rng = Random(self.seed)
        self.n_cells = self.n_rows * self.n_cols
        self.n_filled_cells = 0
        self.score = 0
        self.next_pieces_queue = []
        #if normal mode:
        if self.mode == Mode.NORMAL:
            self.next_pieces_generator = NextPiecesGenerator (self.rng,
                                                              self.n_next_pieces,
                                                              self.n_types)
        elif self.mode == Mode.DISTANCE:
            #if distance mode:
            self.next_pieces_generator = NextPiecesGenerator (self.rng,
                                                              2,
                                                              self.n_types)
        self.drop_delay = 0
        self.generate_next_pieces ()
        self.board = Board (self.n_rows, self.n_cols)
        self.init_board (3)
        self.trace = []
        self.last_move = None
        self.record_trace()


    def generate_next_pieces(self):
        self.next_pieces_queue = self.next_pieces_generator.yield_next_pieces ()
        #TODO: use probablity law
        self.drop_delay = self.rng.randint(0, 3)


    def init_board(self, n):
        """Put n random pieces on the board"""
        for i in range(n):
            p = self.next_pieces_generator.yield_next_piece()
            c = self.rng.choice(self.board.free_cells())
            self.board.set_piece (c.row, c.col, p)
            self.n_filled_cells += 1


    def fill_board (self):
        """remove complete lines, and add next_pieces on the board.
        """
        #in distance mode, only drop if delay is zero

        if self.mode == Mode.DISTANCE and self.drop_delay > 0:
            return
        
        for piece in self.next_pieces_queue:
            if self.check_game_over ():
                return
            c = self.rng.choice(self.board.free_cells())
            self.board.set_piece (c.row, c.col, piece)

            inactivate = self.board.get_cell (c.row, c.col).get_all_directions (self.board.grid, Game.N_MATCH)
            if len(inactivate) > 0:
                self.n_filled_cells -= len(inactivate)
                for cell in inactivate:
                    self.board.set_piece (cell.row, cell.col, None)
                self.update_score (len(inactivate))
            self.n_filled_cells += 1
            
        #generate new pieces to replace the ones we just put on the board
        self.generate_next_pieces ()


    def update_score (self, n_matched):
        self.score += (int) (45 * math.log (0.25 * n_matched))


    def check_game_over (self):
        if self.n_cells - self.n_filled_cells == 0:
            return True
        return False


    def next_step (self, just_scored = False):
        self.record_trace()
        if just_scored:
            if self.mode == Mode.NORMAL:
                return
            elif self.mode == Mode.DISTANCE:
                self.drop_delay +=2
        self.fill_board ()


    def make_move (self, start_row, start_col, end_row, end_col):
        """Make a move on the board.
        
        return True if the move could be completed, False otherwise
        
        In normal mode, after the move is performed, the content of the
        next pieces queue is randomly added on the board.
        
        In distance mode, this method returns either if the move is finished, 
        or if a new piece is added on the board.
        
        """
        path = self.board.find_path (start_row,
                                     start_col,
                                     end_row,
                                     end_col)

        if path is None or len(path) == 0:
            #move is impossible, don't do it
            return
        
        #record move
        self.last_move = (start_row, start_col, end_row, end_col)
        
        #evaluate which event (get to destination vs drop) will happen first
        if self.mode == Mode.DISTANCE and len(path) > self.drop_delay:
            #drop happen first: move to path[self.drop_delay] , then do drop
            #and continue move if new path is not longer
            n_moves = self.drop_delay
            dst = path[n_moves]
            row = dst.row
            col = dst.col
            self.drop_delay = 0
            finished = False
        else:
            #move can be done
            self.drop_delay -= (len(path))
            (row, col) = (end_row, end_col)
            finished = True
        
        #move to (row, col)
        p = self.board.get_piece(start_row, start_col)
        self.board.set_piece (start_row, start_col, None)
        self.board.set_piece (row, col, p)
        
        #execute board logic at (row, col)
        inactivate = self.board.get_cell (row, col).get_all_directions (self.board.grid, Game.N_MATCH)
        if len(inactivate) > 0:
            self.n_filled_cells -= len(inactivate)
            for cell in inactivate:
                self.board.set_piece (cell.row, cell.col, None)
            self.update_score (len(inactivate))
        
        #proceed to fill board
        self.next_step(len(inactivate) > 0)
        
        #if not finished, evaluate new path
        if not finished: #todo check piece still exists
            new_path = self.board.find_path (row,
                                     col,
                                     end_row,
                                     end_col)
            if len(new_path) + n_moves <= len(path):
                self.make_move(row, col, end_row, end_col)


    def record_trace(self):
        """Add current state (board, next_pieces, move, score) to the trace"""
        
        board_data = [c.piece for c in self.board.all_cells()]
        self.trace.append((board_data, self.next_pieces_queue, self.last_move, self.score))
    
        
class Helper:

    def __init__(self, game):
        """Create an helper for game.
        
        >>> g = Game()
        >>> hp = Helper(g)
        >>> hp.board is g.board
        True
        >>> len(hp.neighbourhood)
        7
        >>> len(hp.neighbourhood[0])
        7
        >>> n = hp.neighbourhood[0][0]
        >>> len(n)
        3
        >>> [(c.row, c.col) for c in n[0]]
        [(0, 1), (0, 2), (0, 3), (0, 4)]
        >>> [(c.row, c.col) for c in n[1]]
        [(1, 0), (2, 0), (3, 0), (4, 0)]
        >>> [(c.row, c.col) for c in n[2]]
        [(1, 1), (2, 2), (3, 3), (4, 4)]
        
        >>> n = hp.neighbourhood[6][6]
        >>> len(n)
        3
        
        >>> n = hp.neighbourhood[6][0]
        >>> len(n)
        3
        
        """
        self.board = game.board
        self.n_types = game.n_types
        self.cache = None
        result = list()
        #prepare evalutation neighbourhood
        for r in range(game.n_rows):
            result.append(list())
            for c in range(game.n_cols):
                result[r].append(list())
                for D in range(-2,3):
                    #horizontal
                    if c + D - 2>= 0 and c + D + 2 < game.n_cols:
                        result[r][c].append([self.board.get_cell(r, c+d) 
                                             for d in range(D-2, D+3)
                                             if d != 0])
                    #vertical
                    if r + D - 2>= 0 and r + D + 2 < game.n_rows:
                        result[r][c].append([self.board.get_cell(r+d, c) 
                                             for d in range(D-2, D+3)
                                             if d != 0])
                    #diagonal 1
                    if c + D - 2>= 0 \
                       and r + D - 2>= 0 \
                       and r + D + 2 < game.n_rows \
                       and c + D + 2 < game.n_cols:
                        result[r][c].append([self.board.get_cell(r+d,c+d) 
                                             for d in range(D-2,D+3)
                                             if d != 0])
                    #diagonal 2
                    if c + D - 2 >= 0 \
                       and r - D - 2 >= 0 \
                       and c + D + 2 < game.n_cols \
                       and r - D + 2 < game.n_rows:
                        result[r][c].append([self.board.get_cell(r-d,c+d)
                                             for d in range(D-2,D+3)
                                             if d != 0])
                    
        self.neighbourhood = result


    def actions(self):
        """return all possible actions, in the form of a dictionary,
        with each possible destination cell a key, associated with all the 
        possible source cells
        
        >>> g = MockGame(3,5)
        >>> g.board.set_piece(0, 2, 1)
        >>> g.board.set_piece(1, 2, 2)
        >>> hp = Helper(g)
        >>> act = hp.actions()
        >>> len(act)
        13
        >>> [c.piece is None for c in act.keys()]
        [True, True, True, True, True, True, True, True, True, True, True, True, True]
        >>> [len(act[c]) for c in g.board.free_cells()]
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        >>> g.board.get_cell(0,2) in act[g.board.get_cell(0,0)]
        True
        >>> g.board.get_cell(1,2) in act[g.board.get_cell(0,0)]
        True
        >>> g.board.set_piece(0, 3, 3)
        >>> g.board.set_piece(2, 2, 3)
        >>> g.board.set_piece(2, 3, 2)
        >>> act = hp.actions()
        >>> len(act)
        10
        >>> len(act[g.board.get_cell(0,0)])
        3
        >>> g.board.get_cell(0,2) in act[g.board.get_cell(0,0)]
        True
        >>> g.board.get_cell(1,2) in act[g.board.get_cell(0,0)]
        True
        >>> g.board.get_cell(1,2) in act[g.board.get_cell(0,0)]
        True
        >>> len(act[g.board.get_cell(0,4)])
        3
        >>> g.board.get_cell(0,3) in act[g.board.get_cell(0,4)]
        True
        >>> g.board.get_cell(1,2) in act[g.board.get_cell(0,4)]
        True
        >>> g.board.get_cell(2,3) in act[g.board.get_cell(0,4)]
        True
        >>> act
        
        
        """
        result = dict()
        
        b = self.board
        free = b.free_cells();
        while len(free) > 0:
            c = free.pop()
            #try to grow free cell
            zone = set()
            zone.add(c)
            border = set()
            to_inspect = c.get_neighbours(b.grid)
            while len(to_inspect) > 0:
                c = to_inspect.pop()
                if c.piece is None:
                    #n is free, try to grow
                    if c in free:
                        free.remove(c)
                    zone.add(c)
                    for n in c.get_neighbours(b.grid):
                        if n not in zone:
                            #neighbour not alrady seen, inspect
                            to_inspect.append(n)
                else:
                    #n is part of border
                    border.add(c)
            #zone is finished
            for c in zone:
                if c in result.keys():
                    l = list(result[c])
                    l.extend(list(border))
                    result[c] = l
                else:
                    result[c] = list(border)
        return result


    def build_eval_cache(self):
        """Try to detect alignments, and cache the corresponding move
        evaluation data.
        
        >>> g = MockGame()
        >>> hp = Helper(g)
        >>> g.board.set_piece(0, 0, 1)
        >>> g.board.print()
        |1| | | | | | |
        | | | | | | | |
        | | | | | | | |
        | | | | | | | |
        | | | | | | | |
        | | | | | | | |
        | | | | | | | |
        >>> hp.build_eval_cache()
        >>> hp.cache[0][1]
        {0: 12.0, 1: 115.0, 2: 12.0, 3: 12.0, 4: 12.0}
        >>> hp.cache[3][3]
        {0: 44.0, 1: 147.0, 2: 44.0, 3: 44.0, 4: 44.0}
        """
        result = []
        for r in range(self.board.n_rows):
            result.append(list())
            for c in range(self.board.n_cols):
                result[r].append(list())
                result[r][c] = dict()
                for t in range(self.n_types):
                    v = 0
                    for mask in self.neighbourhood[r][c]:
                        same = 0
                        free = 0
                        for cell in mask:
                            if cell.piece:
                                if cell.piece == t:
                                    same += 1
                            else:
                                free += 1
                        diff = 4 - same - free
                        if same > diff:
                            v = max(v, math.pow(same - diff + 1, 2)*10 + free)
                    result[r][c][t] = v
        self.cache = result


    def eval_move(self, piece, to_row, to_col):
        """Return an evaluation of moving a piece at
        a new position
        """
        if (self.cache is None):
            self.build_eval_cache()
        return self.cache[to_row][to_col][piece]


    def reachable_cells(self, from_row, from_col):
        """Return the list of reachables cells
        """
        return [to for to in self.board.free_cells()
                if self.reachable(from_row, from_col, to.row, to.col)]
        


    def reachable(self, from_row, from_col, to_row, to_col):
        path = self.board.find_path(from_row, from_col, to_row, to_col)
        return (len(path) > 0)


if __name__=='__main__':
    import doctest
    class MockGame():
        def __init__(self, n_rows=7, n_cols=7):
            self.n_types = 5
            self.board = Board(n_rows, n_cols)
            self.n_rows = n_rows
            self.n_cols = n_cols
    doctest.testmod()




