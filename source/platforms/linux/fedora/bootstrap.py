r"""chef bootstrap module for fedora distributions"""

from platforms.linux.common import *
from platforms.linux.redhat.common import *


MIN_VERSION = ('8')


def main(opts, args):
    check_version(opts.dist, MIN_VERSION)
    gem_install_chef(opts, args)
