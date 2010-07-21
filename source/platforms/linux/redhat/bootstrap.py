
from util import *
from platforms.linux.redhat.common import *

MIN_VERSION = ('5', '5')


def install_repository(opts, args):
    check_version(opts.dist, MIN_VERSION)
    
    for repo in REPOSITORIES:
        install_repo[repo['url']]

    
def main(*args):
    install_repository(*args)
    install_chef(*args)
    