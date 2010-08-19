#!/usr/bin/env python2.4
r"""Primary bootstrap module. Parses arguments and proceeds to the os-level
bootstrap module.
"""

import sys, os.path, optparse

import util


def configure(argv):
    r"""Parses command-line arguments"""
    parser = optparse.OptionParser()
    parser.add_option("-o", "--os", dest="os", metavar="OS",
                      help="specify one of [linux] to override detection")
    parser.add_option("-d", "--dist", dest="dist", metavar="DIST",
                      help="specify os-specific distribution")
    parser.add_option("-s", "--server", dest="server", action="store_true",
                      default=False, help="install the Chef server")
    parser.add_option("-w", "--webui", dest="webui", action="store_true",
                      default=False, help="install the Chef server webui")
    parser.add_option("-u", "--url", dest="url", metavar="URL",
                      help="specify the Chef server url")
    parser.add_option("-c", "--name", dest="name", metavar="NAME",
                      help="specify the Chef client name")
    parser.add_option("-v", "--validation", dest="validation", metavar="FILE",
                      help="use as the Chef server validation key")
    return parser.parse_args()


def main(argv):
    
    # add root package to PYTHONPATH
    sys.path.insert(0, os.path.dirname(__file__))
    
    opts, args = configure(argv)
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
