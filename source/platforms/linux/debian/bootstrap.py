
from platforms.linux.common import *
from platforms.linux.debian.common import *

MIN_VERSION = ('5', '0', '5')
# TODO: I don't know how to detect the testing and unstable versions
CHEF_REPOSITORY_COMPONENTS = ('lenny', 'main')

# Note: chef-server WILL NOT install on Debian lenny

def install_repository(opts, args):
    check_version(opts.dist, MIN_VERSION)
    
    repo = ['deb', CHEF_REPOSITORY]
    repo.extend(CHEF_REPOSITORY_COMPONENTS)
    repo = ' '.join(repo)
    add_repo(repo)
    
    add_key(CHEF_REPOSITORY_KEY)
    apt_update()


def main(*args):
    install_repository(*args)
    install_chef(*args)
    
