#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pieces and random pieces generator
"""

from random import randrange

__author__="Rémi Pannequin"
__copyright__ = "Copyright 2020"
__credits__ = ["Rémi Pannequin"]
__license__ = "GPL"
__maintainer__ = "Rémi Pannequin"
__email__ = "remi.pannequin@gmail.com"
__status__ = "Development"

class NextPiecesGenerator:


    def __init__(self, n_next_pieces, n_types):
        """Create a new pieces generator.
        
        >>> g = NextPiecesGenerator(3,5)
        >>> g.pieces
        []
        >>> g.n_next_pieces
        3
        >>> g.n_types
        5
        
        """
        self.pieces = list()
        self.n_next_pieces = n_next_pieces
        self.n_types = n_types


    def _yield_next_piece (self):
        return randrange (self.n_types)


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
            id = self._yield_next_piece ()
            self.pieces.append(id)
        return self.pieces


if __name__=='__main__':
    import doctest
    doctest.testmod()
    
    
