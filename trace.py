#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""see what is in the trace database
"""

import shelve
from datetime import datetime

with shelve.open('trace.db') as db:
    for k in db.keys():
        #date = datetime(k)
        d = db[k]
        print("%s\t%s\t%s\t%d moves\t%s " % (k,  d['score'], d['seed'], len(d['trace']), d['mode']))
        
        
