#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""see what is in the trace database
"""

import shelve

with shelve.open('trace.db') as db:
    for k in db.keys():
        print("%s (score %d)" % (k,  db[k]['score']))
