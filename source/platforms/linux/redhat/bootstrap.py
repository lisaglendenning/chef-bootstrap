
import subprocess, urllib, shutil, time, re

REDHAT_MIN_VERSION = ('5', '5')

REPOSITORIES = [{'name': 'epel', 
                 'url':'http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-3.noarch.rpm'},
                 {'name': 'elff',
                  'url': 'http://download.elff.bravenet.com/5/i386/elff-release-5-3.noarch.rpm'}]
CHEF_CLIENT_PACKAGES = ['chef',]

def execute(args, **kwargs):
    child = subprocess.Popen(args, **kwargs)
    child.communicate()
    if child.returncode != 0:
        raise RuntimeError("%s: returned %d" % (' '.join(args), child.returncode))

def install_repository(argv, system, dist):
    version = tuple(dist[1].split('.'))
    if version < REDHAT_MIN_VERSION:
        raise RuntimeError('Red Hat version %s < %s' % (version, REDHAT_MIN_VERSION))
    
    # install needed repositories
    for repo in REPOSITORIES:
        args = ['rpm', '-Uvh', repo['url']]
        execute(args)
    
def install_chef(argv, system, dist):
    args = ['yum', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    execute(args)
    
def main(*args):
    install_repository(*args)
    install_chef(*args)
    