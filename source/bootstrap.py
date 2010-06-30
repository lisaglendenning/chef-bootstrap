#!/usr/bin/env python2.4

import sys

def main(argv):
    
    # Determine what platform we're on
    plat = sys.platform
    mod = __import__('.'.join(['platforms', plat]), fromlist=plat)
    mod.main(argv)

if __name__ == '__main__':
    main(sys.argv)