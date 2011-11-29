r"""chef bootstrap module for redhat distributions"""

from platforms.linux.redhat.common import *


MIN_VERSION = ('5', '5')


def main(opts, args):
    # Validate OS version
    if check_fedora(opts, args):
        opts.dist = tuple(['fedora'] + list(opts.dist[1:]))
        import platforms.linux.fedora.bootstrap as mod
        return mod.main(opts, args)
    version = tuple(opts.dist[1].split('.'))
    if version < MIN_VERSION:
        raise RuntimeError('%s version %s < %s' % (opts.dist[0], version, MIN_VERSION))
    
    install_support(opts, args)
    install_chef(opts, args)
