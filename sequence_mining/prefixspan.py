#! /usr/bin python

"""
Usage:
    prefixspan.py (frequent | top-k) <threshold>
"""

from __future__ import print_function

import sys
from collections import defaultdict
from heapq import heappop, heappush

from docopt import docopt

results = []

def frequent_rec(patt, mdb, level):
    print ("patt")
    print (patt)
    print ("mdb")
    print (mdb)
    print ("level")
    print (level)
    results.append((len(mdb), patt))

    occurs = defaultdict(list)
    for (i, startpos) in mdb:
        seq = db[i]
        for j in xrange(startpos, len(seq)):
            l = occurs[seq[j]]
            if len(l) == 0 or l[-1][0] != i:
                l.append((i, j + 1))

    for (c, newmdb) in occurs.iteritems():
	print ("c")
	print (c)
        if len(newmdb) >= minsup:
	    print ("patt + c")
	    print (patt + [c])
            frequent_rec(patt + [c], newmdb, level + 1)

def topk_rec(patt, mdb):
    heappush(results, (len(mdb), patt))
    if len(results) > k:
        heappop(results)

    occurs = defaultdict(list)
    for (i, startpos) in mdb:
        seq = db[i]
        for j in xrange(startpos, len(seq)):
            l = occurs[seq[j]]
            if len(l) == 0 or l[-1][0] != i:
                l.append((i, j + 1))

    for (c, newmdb) in sorted(occurs.iteritems(), key=(lambda (c, newmdb): len(newmdb)), reverse=True):
        if len(results) == k and len(newmdb) <= results[0][0]:
            break

        topk_rec(patt + [c], newmdb)

if __name__ == "__main__":
    argv = docopt(__doc__)

    # db = [
        # [int(v) for v in line.rstrip().split(' ')]
        # for line in sys.stdin
    # ]
    db = [
        [1, 2, 7, 8, 9],
        [1, 2, 7, 9, 8],
        [2, 1, 8, 7, 9]
    ]
    """

    db = []
    for i in range (1 , 4):
        tmp = []
        #file_name = "test_file_2/" + str(i) + ".txt"
        file_name = "left_block_file_folder/" + str(i) + ".txt"
        print (file_name)
        
        fl = open (file_name, "r")
        for line in fl.readlines():
        	line = line.replace ("\n", "") 
        	line = line.replace ("block_", "") 
        	tmp.append (int(line))			
        db.append(tmp)	
        fl.close()
    print (db)
    """
    
    if argv["frequent"]:
        minsup = int(argv["<threshold>"])
        f = frequent_rec
    elif argv["top-k"]:
        k = int(argv["<threshold>"])
        f = topk_rec

    print ("step 1 finish")

    f([], [(i, 0) for i in xrange(len(db))], 0)

    print ("step 2 finish")
    if argv["top-k"]:
        results.sort(key=(lambda (freq, patt): (-freq, patt)))
    for (freq, patt) in results:
	print("{}: {}".format(patt, freq))

