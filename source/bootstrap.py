#!/usr/bin/env python2.4

import sys, platform

def main(argv):
    
    # Detect the OS
    system = platform.system()
    try:
        mod = __import__('.'.join([__package__, 'platforms', system, 'bootstrap']),
                         fromlist='bootstrap')
    except ImportError:
        raise RuntimeError("Unsupported system: %s" % system)
    else:
        mod.main(argv, system)

if __name__ == '__main__':
    main(sys.argv)
