r"""Determines distribution and proceeds to appropriate module"""

import sys, os.path

import util

def main(opts, args):
    
    # add linux package to PYTHONPATH
    sys.path.insert(0, os.path.dirname(__file__))
    
    if opts.dist:
        try:
            opts.dist = tuple(opts.dist.split(','))
        except Exception:
            raise ValueError(opts.dist)
    else:
        opts.dist = util.guess_dist(opts.os)
        
    # attempts to import and run the bootstrap module for the specific distribution
    try:
        package = __name__.rsplit('.', 1)[0]
        modname = opts.dist[0].lower()
        mod = __import__('.'.join([package, modname, 'bootstrap']), 
                         globals(), locals(), 'bootstrap')
        mod.main(opts, args)
    except ImportError:
        raise RuntimeError("Unsupported %s distribution: %s" % (opts.os, opts.dist))
