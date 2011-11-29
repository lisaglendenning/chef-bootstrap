#!/usr/bin/env python2.4
r"""Entry module. Parses arguments and proceeds to the os-level bootstrap module.
"""

import sys, os.path, optparse, platform


def configure(argv):
    r"""Parses command-line arguments"""
    parser = optparse.OptionParser()
    parser.add_option("-o", "--os", dest="os", metavar="OS",
                      help="specify one of [linux] to override detection")
    parser.add_option("-d", "--dist", dest="dist", metavar="DIST",
                      help="specify OS-specific distribution")
    parser.add_option("-a", "--arch", dest="arch", metavar="ARCH",
                      help="specify system architecture")
    parser.add_option("-s", "--server", dest="server", action="store_true",
                      default=False, help="install the Chef server")
    parser.add_option("-w", "--webui", dest="webui", action="store_true",
                      default=False, help="install the Chef server webui")
    parser.add_option("-u", "--url", dest="url", metavar="URL",
                      default='http://localhost:4000', 
                      help="specify the Chef server url")
    return parser.parse_args(argv)


def main(argv):
    # process options
    opts, args = configure(argv)
    if opts.os is None:
        opts.os = platform.system().lower()
    if opts.arch is None:
        opts.arch = platform.machine()
    
    # add this package to PYTHONPATH
    sys.path.insert(0, os.path.dirname(__file__))
    # import system specific module
    try:
        mod = __import__('.'.join(['platforms', opts.os, 'bootstrap']),
                         globals(), locals(), 'bootstrap')
    except ImportError:
        raise RuntimeError("Unsupported system: %s" % opts.os)
    else:
        return mod.main(opts, args)


if __name__ == '__main__':
    main(sys.argv)
