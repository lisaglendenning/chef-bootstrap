#!/usr/bin/env python2.4

import sys, platform

def main(argv):
    
    # Detect the OS
    system = platform.system()
    try:
        modname = system.lower()
        mod = __import__('.'.join(['platforms', modname, 'bootstrap']),
                         globals(), locals(), 'bootstrap')
    except ImportError:
        raise RuntimeError("Unsupported system: %s" % system)
    else:
        mod.main(argv, system)

if __name__ == '__main__':
    main(sys.argv)
