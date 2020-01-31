from game import Game, Helper
import random
import os.path as path

def heuristic_0(hp, act):
    """Heuristic player: selected move is the one with the biggest score between
    source and destination.
    
    act : collection of all posible actions
    """
    #search best move (highest difference of eval)
    best = None
    for dst in act.keys():
        for src in act[dst]:
            eval_dst = hp.eval_move(src.piece, dst.row, dst.col)
            if best is None or best < eval_dst:
                best = eval_dst
                best_dst = dst
                best_src = src
    return (best_src, best_dst)


def heuristic_1(hp, act):
    """Heuristic player: 
     * first destination cell is selected (best score),
     * then the source with the lowest score is selected
    """
    #search best destination (highest eval)
    best = None
    for dst in act.keys():
        #extract possible types
        types = set([c.piece for c in act[dst]])
        for t in types:
            eval_dst = hp.eval_move(t, dst.row, dst.col)
            if best is None or best < eval_dst:
                best = eval_dst
                best_type = t
                best_dst = dst
    #search best source for this destination (lowest eval)
    best = None
    for src in act[best_dst]:
        if src.piece == best_type:
            eval_src = hp.eval_move(src.piece, src.row, src.col) 
            if best is None or best > eval_src:
                best = eval_src
                best_src = src
    return (best_src, best_dst)


def heuristic_2(hp, act):
    """Heuristic player: selected move is the one with the biggest score between
    source and destination.
    
    act : collection of all posible actions
    """
    #search best move (highest difference of eval)
    best = None
    for dst in act.keys():
        for src in act[dst]:
            eval_dst = hp.eval_move(src.piece, dst.row, dst.col)
            eval_src = hp.eval_move(src.piece, src.row, src.col) 
            if best is None or best < (eval_dst - eval_src):
                best = eval_dst - eval_src
                best_dst = dst
                best_src = src
    return (best_src, best_dst)


def best_destination(hp, act):
    """Search the best destination.
    Return a tupple (row, col, type)"""
    best = None
    for dst in act.keys():
        for src in act[dst]:
            eval_dst = hp.eval_move(src.piece, dst.row, dst.col)
            if best is None or best < eval_dst:
                best = eval_dst
                best_dst = dst
                t = src.piece.id
                
    return (best_dst.row, best_dst.col, t)
    

def heuristic_player(g, h, log=False):
    hp = Helper(g)
    mem = []
    while not g.check_game_over():
        act = hp.actions()
        #display current state
        if log:
            print("next: %s" % [p.id for p in g.next_pieces_queue])
            g.board.print()
        #search best action
        hp.build_eval_cache()
        (src, dst) = h(hp, act)
        #apply action
        if log:
            print("moving %d from %s to %s" % (src.piece.id, (src.row, src.col), (dst.row, dst.col)))
        g.make_move(src.row, src.col, dst.row, dst.col)
        if log:
            g.board.print()
            print("================================================================")
        mem.append(g.board.grid)
    return g.score


def step(g):
    hp = Helper(g)
    act = hp.actions()
    #search best action
    hp.build_eval_cache()
    (src, dst) = heuristic_2(hp, act)
    #apply action
    g.make_move(src.row, src.col, dst.row, dst.col)
    
    

if __name__=='__main__':
    import matplotlib
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.io
    
    scores = []
    for i in range(1000):
        g = Game()
        scores.append(heuristic_player(g, heuristic_2, False))
        print('game %s' % i)
        
    print("moyenne:")
    print(sum(scores)/len(scores))    
    
    #if path.isfile('heuristic.mat'):
    #    mat = scipy.io.loadmat('heuristic.mat')
    #    scores = mat['score'].tolist()[0] + scores
    #scipy.io.savemat('heuristic.mat', {'score':scores})
    
    
    
    num_bins = 20
    fig, ax = plt.subplots()

    # the histogram of the data
    n, bins, patches = ax.hist(scores, num_bins, density=1)


    ax.set_xlabel('Score')
    ax.set_ylabel('Probability density')
    ax.set_title(r'Score for heuristic player (n = %d)' % len(scores))

    # Tweak spacing to prevent clipping of ylabel
    fig.tight_layout()
    plt.show()
