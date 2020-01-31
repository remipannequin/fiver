#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Board and Cells of the board
"""

from enum import Enum, auto


__author__="Rémi Pannequin"
__copyright__ = "Copyright 2020"
__credits__ = ["Rémi Pannequin"]
__license__ = "GPL"
__maintainer__ = "Rémi Pannequin"
__email__ = "remi.pannequin@gmail.com"
__status__ = "Development"

class Board:

    def __init__(self, n_rows, n_cols):
        """Create a new board
        
        >>> b = Board(7, 9)
        >>> b.n_rows
        7
        >>> b.n_cols
        9
        >>> b.grid is not None
        True
        >>> len(b.grid)
        7
        >>> [len(row) for row in b.grid]
        [9, 9, 9, 9, 9, 9, 9]
        """
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.grid = [[Cell(row, col) for col in range(n_cols)] for row in range(n_rows)]


    def print(self):
        """Pretty print a row of the board
        
        >>> b = Board(7, 9)
        >>> b.print()
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | | | |
        >>> b.set_piece(3, 7, Piece(2))
        >>> b.print()
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | |2| |
        | | | | | | | | | |
        | | | | | | | | | |
        | | | | | | | | | |
        """
        for row in self.grid:
            p = []
            for c in row:
                if c.piece:
                    p.append("%d"%c.piece.id)
                else:
                    p.append(" ")
            print("|"+"|".join(p)+"|")


    def get_grid (self):
        return self.grid


    def set_piece (self, row, col, piece = None):
        """put a piece at (row, col). This should be empty if piece is not None
        
        >>> b = Board(7, 9)
        >>> p = Piece(3)
        >>> b.set_piece(3, 7, p)
        >>> b.grid[3][7].piece.id
        3
        """
        if piece:
            assert self.grid[row][col].piece == None
        self.grid[row][col].piece = piece


    def get_piece (self, row, col):
        """Return the piece at row, col.
        
        >>> b= Board(5, 5)
        >>> b.get_piece(0, 0) is None
        True
        >>> b.set_piece(0,0, Piece(1))
        >>> b.get_piece(0, 0).id
        1
        """
        return self.grid[row][col].piece


    def get_cell (self, row, col):
        assert(row >= 0)
        assert(row < self.n_rows)
        assert(col >= 0)
        assert(col < self.n_cols)
        return self.grid[row][col]


    def all_cells(self):
        """Return a list of all cells in the board
        
        >>> b = Board(4,4)
        >>> len(b.all_cells())
        16
        
        """
        return  [c for row in self.grid for c in row]


    def occupied_cells(self):
        """Return a list of occupied cells
        >>> b = Board(4,4)
        >>> len(b.occupied_cells())
        0
        >>> b.set_piece(0,0, Piece(1))
        >>> c = b.occupied_cells()
        >>> (c[0].row, c[0].col, c[0].piece.id)
        (0, 0, 1)
        >>> b.set_piece(1,1, Piece(2))
        >>> c = b.occupied_cells()
        >>> len(c)
        2
        >>> (c[1].row, c[1].col, c[1].piece.id)
        (1, 1, 2)
        
        """
        return [c for c in self.all_cells() if c.piece is not None]


    def free_cells(self):
        """Return a list of free cells
        >>> b = Board(4,4)
        >>> len(b.free_cells())
        16
        >>> b.set_piece(0,0, Piece(1))
        >>> c = b.free_cells()
        >>> len(c)
        15
        >>> Cell(0,0) in c
        False
        
        """
        return [c for c in self.all_cells() if c.piece is None]


    def find_path (self, 
                   start_row,
                   start_col,
                   end_row,
                   end_col):
        """Return the path between start and end
        
        >>> b = Board(7, 7)
        >>> p = b.find_path(0, 0, 6, 6)
        >>> len(p)
        12
        
        >>> b = Board(7, 7)
        >>> b.set_piece(0, 1, Piece(1))
        >>> b.set_piece(1, 1, Piece(1))
        >>> b.set_piece(1, 0, Piece(1))
        >>> b.find_path(0, 0, 5, 2)
        []
        
        >>> b = Board(3, 5)
        >>> b.set_piece(0, 3, Piece(1))
        >>> b.set_piece(2, 3, Piece(1))
        >>> b.find_path(1, 0, 1, 4)
        [Cell(1, 1), Cell(1, 2), Cell(1, 3), Cell(1, 4)]
        >>> b.set_piece(1, 3, Piece(1))
        >>> b.find_path(0, 0, 2, 2)
        [Cell(0, 1), Cell(0, 2), Cell(1, 2), Cell(2, 2)]
        >>> b.find_path(0, 0, 2, 4)
        []
        
        """
        self._reset_path_search()
        src = self.grid[start_row][start_col]
        dst = self.grid[end_row][end_col]
        closed = list()
        open = list()
        open.append(src)
        current_cell = None
        current_cost = 0
        path = []
        
        while len(open) != 0:
            current_cost = len(closed)

            current_cell = Board.best_candidate (open, current_cost, dst)
            closed.append(current_cell)
            open.remove (current_cell)

            if dst in closed:
                p = dst;
                while p.parent:
                    path.insert (0, p)
                    p = p.parent
                return path

            neighbours = current_cell.get_neighbours_free (self.grid)
            for neighbour in neighbours:
                # if self adjacent square is already in the closed list ignore it
                if neighbour in closed:
                    continue

                # if its not in the open list add it
                if neighbour not in open:
                    neighbour.parent = current_cell
                    open.append(neighbour)

                # if its already in the open list and using the current score makes it lower,
                # update the parent because it means it is a better path
                else:
                    if Board.total_cost (neighbour, dst, current_cost) < neighbour.cost:
                        neighbour.parent = current_cell
                        neighbour.cost = total_cost (neighbour, dst, current_cost)
        return path


    def cell_equal (a, b):
        if a and b:
            return a == b
        return false


    def _reset_path_search (self):
        for row in self.grid:
            for cell in row:
                cell.parent = None
                cell.cost = float('+Inf')
                
                
    def best_candidate (neighbours, current_cost, end):
        """f = g + h, where f is the cost of the road
        g is the movement cost from the start cell to the current square
        h is the estimated movement cost from the current square to the destination cell
        """
        lowest_f = float('inf')
        best_candidate = None

        for neighbour in neighbours:
            neighbour.cost = Board.total_cost (neighbour, end, current_cost)

            if neighbour.cost < lowest_f:
                lowest_f = neighbour.cost
                best_candidate = neighbour

        return best_candidate


    def manhattan (start_x, start_y, end_x, end_y):
        """for h it is used the Manhattan distance
        the sum of the absolute values of the differences of the coordinates.
        if start = (start_x, start_y) and end = (end_x, end_y)
        => h = |start_x - end_x| + |start_y - end_y|
        """
        return abs(start_x - end_x) + abs(start_y - end_y)


    def total_cost (start, end, current_cost):
        g = current_cost + 1
        h = Board.manhattan (start.row, start.col, end.row, end.col)
        f = g + h
        return f


class Cell:

    def __init__(self, row, col, parent = None, piece = None):
        self.row = row
        self.col = col
        self.parent = parent
        self.piece = piece
        self.cost = float('inf')


    def __eq__(self, cell):
        if cell:
            return self.row == cell.row and self.col == cell.col
        return False


    def __hash__(self):
        return hash(self.row) + hash(self.col)


    def __repr__(self):
        return "Cell(%d, %d)" % (self.row, self.col)

    def get_neighbour(self, board, dir):
        neighbour = None
        row = -1 
        col = -1
        
        if dir == Direction.RIGHT:
            row = self.row
            col = self.col + 1
        elif dir == Direction.LEFT:
            row = self.row
            col = self.col - 1
        elif dir == Direction.UP:
            row = self.row - 1
            col = self.col
        elif dir ==  Direction.DOWN:
            row = self.row + 1
            col = self.col
        elif dir ==  Direction.UPPER_LEFT:
            row = self.row - 1
            col = self.col - 1
        elif dir ==  Direction.LOWER_RIGHT:
            row = self.row + 1
            col = self.col + 1
        elif dir ==  Direction.UPPER_RIGHT:
            row = self.row - 1
            col = self.col + 1
        elif dir ==  Direction.LOWER_LEFT:
            row = self.row + 1
            col = self.col - 1
        
        if row >= 0 and row < len(board) and col >= 0 and col < len(board[0]):
            neighbour = board[row][col]
        return neighbour


    def get_neighbours_free (self, board):
        """Return a list of all the free neighbours of this cell 
        (diagonal not considered as neighbours)
        
        
        """
        neighbours = []
        right = None
        left = None
        up = None
        down = None

        right = self.get_neighbour (board, Direction.RIGHT)
        if right != None and right.piece == None:
            neighbours.append(right)

        left = self.get_neighbour (board, Direction.LEFT)
        if left != None and left.piece == None:
            neighbours.append(left)

        up = self.get_neighbour (board, Direction.UP)
        if up != None and up.piece == None:
            neighbours.append(up)

        down = self.get_neighbour (board, Direction.DOWN)
        if down != None and down.piece == None:
            neighbours.append(down)

        return neighbours


    def get_neighbours (self, board):
        neighbours = []
        right = None
        left = None
        up = None
        down = None

        right = self.get_neighbour (board, Direction.RIGHT)
        if right != None:
            neighbours.append(right)

        left = self.get_neighbour (board, Direction.LEFT)
        if left != None:
            neighbours.append(left)

        up = self.get_neighbour (board, Direction.UP)
        if up != None:
            neighbours.append(up)

        down = self.get_neighbour (board, Direction.DOWN)
        if down != None:
            neighbours.append(down)

        return neighbours


    def _get_direction (self, board, dir, l):
        """Return the set of cell that have the same piece"""
        if l is None:
            l = set()
        cell = self
        while cell and cell.piece != None and cell.piece == self.piece:
            l.add(cell)
            cell = cell.get_neighbour (board, dir)
        return l


    def _get_horizontal (self, board):
        l = self._get_direction (board, Direction.LEFT, None)
        l = self._get_direction (board, Direction.RIGHT, l)
        return l


    def _get_vertical (self, board):
        l = self._get_direction (board, Direction.UP, None)
        l = self._get_direction (board, Direction.DOWN, l)
        return l


    def _get_first_diagonal (self, board):
        l = self._get_direction (board, Direction.UPPER_LEFT, None)
        l = self._get_direction (board, Direction.LOWER_RIGHT, l)
        return l


    def _get_second_diagonal (self, board):
        l = self._get_direction (board, Direction.UPPER_RIGHT, None)
        l = self._get_direction (board, Direction.LOWER_LEFT, l)
        return l


    def get_all_directions (self, board, n_match):
        """Return all lines (horizontal, vertical, diagonals) with more
        pieces than n_match
        
        >>> b = Board(7, 7)
        >>> b.set_piece(1, 1, Piece(1))
        >>> b.set_piece(1, 2, Piece(1))
        >>> b.set_piece(1, 3, Piece(1))
        >>> b.set_piece(1, 4, Piece(1))
        >>> c= b.get_cell(1,4)
        >>> r = c.get_all_directions(b.grid, 4)
        >>> len(r)
        4
        >>> [c.piece.id for c in r]
        [1, 1, 1, 1]
        
        """
        inactivate = set()

        l = self._get_horizontal (board)
        if len(l) >= n_match:
            inactivate = inactivate.union(l)

        l = self._get_vertical (board)
        if len(l) >= n_match:
            inactivate = inactivate.union(l)

        l = self._get_first_diagonal (board)
        if len(l) >= n_match:
            inactivate = inactivate.union(l)

        l = self._get_second_diagonal (board)
        if len(l) >= n_match:
            inactivate = inactivate.union(l)
        return inactivate


class Direction(Enum):
    RIGHT= auto()
    LEFT= auto()
    UP= auto()
    DOWN= auto()
    UPPER_RIGHT= auto()
    LOWER_LEFT= auto()
    UPPER_LEFT= auto()
    LOWER_RIGHT= auto()
    
    
    
    
    
if __name__=='__main__':
    import doctest
    from piecegenerator import Piece
    doctest.testmod()
    
    
    
    
    
    

