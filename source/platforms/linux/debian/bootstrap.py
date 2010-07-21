
import urllib

from util import *
from platforms.linux.debian.common import *

MIN_VERSION = ('5', '0', '5')
# TODO: I don't know how to detect the testing and unstable versions
CHEF_REPOSITORY_COMPONENTS = ('lenny', 'main')

def install_repository(opts, args):
    check_version(opts.dist, MIN_VERSION)
    
    repo = ['deb', CHEF_REPOSITORY]
    repo.extend(CHEF_REPOSITORY_COMPONENTS)
    repo = ' '.join(repo)
    add_repo(repo)
    
    # add key
    keyfile, headers = urllib.urlretrieve(CHEF_REPOSITORY_KEY)
    args = ['apt-key', 'add', keyfile]
    execute(args)

    # update packages
    args = ['apt-get', 'update']
    execute(args)


def main(*args):
    install_repository(*args)
    install_chef(*args)
    