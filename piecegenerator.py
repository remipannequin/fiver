from random import randrange

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
        >>> [p.id >= 0 and p.id < 5 for p in g.pieces]
        [True, True, True]
        """
        self.pieces.clear ()
        for i in range(self.n_next_pieces):
            id = self._yield_next_piece ()
            self.pieces.append(Piece (id))
        return self.pieces



class Piece:

    def __init__(self, id):
        """Create a new Piece with id.
        
        >>> p = Piece(1)
        >>> p.id
        1
        
        """
        self.id = id


    def __eq__ (self, piece):
        """Test whether two pieces are the same, i.e. they have the same id
        
        >>> Piece(1) == Piece(1)
        True
        
        >>> Piece(1) == Piece(2)
        False
        
        >>> Piece(1) == None
        False
        
        """
        if piece:
            return self.id == piece.id
        return False

    def __hash__(self):
        return hash(self.id)


if __name__=='__main__':
    import doctest
    doctest.testmod()
    
    
