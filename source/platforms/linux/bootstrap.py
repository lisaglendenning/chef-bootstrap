r"""Determines distribution and proceeds to appropriate module"""

import platform

def main(opts, args):
    # validate options
    if opts.dist is None:
        opts.dist = platform.dist()
    else:
        try:
            opts.dist = tuple(opts.dist.split(','))
        except Exception:
            raise ValueError(opts.dist)
    opts.dist = tuple([opts.dist[0].lower()] + list(opts.dist[1:]))
    opts.arch.replace(' ', '_')

    # run bootstrap module for the specific distribution
    try:
        mod = __import__('.'.join(['platforms', 'linux', opts.dist[0], 'bootstrap']), 
                         globals(), locals(), 'bootstrap')
    except ImportError:
        raise RuntimeError("Unsupported %s distribution: %s" % (opts.os, opts.dist[0]))
    else:
        return mod.main(opts, args)
