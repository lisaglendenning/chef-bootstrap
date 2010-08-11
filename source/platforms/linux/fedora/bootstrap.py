
from platforms.linux.common import *
from platforms.linux.redhat.common import *


MIN_VERSION = ('8')


def main(*args):
    check_version(opts.dist, MIN_VERSION)
    install_rubygems(opts, args)
    bootstrap_chef(opts, args)
