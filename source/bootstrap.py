#!/usr/bin/env python2.4
r"""Primary bootstrap module. Parses arguments and proceeds to the os-level
bootstrap module.
"""

import sys, os.path, optparse

import util


def main(argv):
    
    # add root package to PYTHONPATH
    sys.path.insert(0, os.path.dirname(__file__))
    
    opts, args = util.configure(argv)
    if not opts.url:
        opts.url = "http://127.0.0.1:4000"
    if not opts.os:   
        opts.os = util.guess_os()
    try:
        mod = __import__('.'.join(['platforms', opts.os, 'bootstrap']),
                         globals(), locals(), 'bootstrap')
    except ImportError:
        raise RuntimeError("Unsupported system: %s" % opts.os)
    else:
        mod.main(opts, args)


if __name__ == '__main__':
    main(sys.argv)
