
from platforms.linux.common import *
from platforms.linux.redhat.common import *


MIN_VERSION = ('5', '5')


def main(opts, args):
    if check_fedora(opts, args):
        import platforms.linux.fedora.bootstrap as mod
        mod.main(opts, args)
    else:
        check_version(opts.dist, MIN_VERSION)
        for repo in REPOSITORIES:
            install_remote_rpm(repo['url'])
        install_chef(opts, args)
