#!/usr/bin/env python2.4

import sys, platform

def main(argv):
    
    # Detect the OS
    system = platform.system().lower()
    try:
        mod = __import__('.'.join(['platforms', system, 'bootstrap']),
                         globals(), locals(), 'bootstrap')
    except ImportError:
        raise RuntimeError("Unsupported system: %s" % system)
    else:
        mod.main(argv, system)

if __name__ == '__main__':
    main(sys.argv)
