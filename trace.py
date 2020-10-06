#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""see what is in the trace database

    Usage:
        trace.py histo [-m MODE][-s SEED] [-a MIN_SCORE] [-b MAX_SCORE]
        trace.py plot_free [-m MODE][-s SEED] [-a MIN_SCORE] [-b MAX_SCORE]
        trace.py plot_score [-m MODE][-s SEED] [-a MIN_SCORE] [-b MAX_SCORE]
        
    Options:
        -m MODE
        -s SEED
        -a MIN_SCORE select games with score above MIN_SCORE
        -b MAX_SCORE select games with score below MAX_SCORE
"""

import shelve
from datetime import datetime
import operator

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import scipy.io
from docopt import docopt

args = docopt(__doc__)
print(args)

data = []

def filter(d):
    if args['-s'] and d['seed'] != int(args['-s']):
        return False
    if args['-m'] and d['mode'] != args['-m']:
        return False
    if args['-a'] and d['score'] < int(args['-a']):
        return False
    if args['-b'] and d['score'] > int(args['-b']):
        return False
    return True



with shelve.open('trace.db') as db:
    for k in db.keys():
        if filter(db[k]):
            d = db[k]
            data.append(d)
            print("%s\t%s\t%s\t%d moves\t%s " % (k,  d['score'], d['seed'], len(d['trace']), d['mode']))
    
    

scores = [d['score'] for d in data]
traces = [d['trace'] for d in data]
nb_free = [[tr[0].count(None) for tr in trace] for trace in traces]

if args['histo']:
    
    
    
    num_bins = 25
    fig, ax = plt.subplots()

    # the histogram of the data
    n, bins, patches = ax.hist(scores, num_bins, density=1)


    ax.set_xlabel('Score')
    ax.set_ylabel('Probability density')
    ax.set_title(r'Score in normal mode (n = %d)' % len(scores))

    # Tweak spacing to prevent clipping of ylabel
    fig.tight_layout()
    plt.show()
    exit()

if args['plot_free']:
    
    
    
    
    fig, ax = plt.subplots()
    for y in nb_free:
        ax.plot(y)
    ax.set_ylabel('Number of free cells')
    ax.set_xlabel('Moves')
    ax.set_title(r'Number of free cells (%d games)' % len(traces))
    plt.show()
    exit()

if args['plot_score']:

    fig, ax = plt.subplots()
    data = []
    for nb in nb_free:
        y = list(map(operator.sub,nb[1:], nb[:-1]))
        d = [nb[i-1] for i in range(1,len(nb)) if y[i-1] > 0]
        data.extend(d)
    nb_bins = max(data) - min(data)
    ax.hist(data, nb_bins, density=1)
    ax.set_ylabel('probabity to score')
    ax.set_xlabel('Number of free cells (before score')
    ax.set_title(r'Probability to score (%d games)' % len(traces))
    plt.show()
    exit()
    
    

    
