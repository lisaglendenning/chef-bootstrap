
import os.path, subprocess, shutil, time

from util import *

REPOSITORIES = [{'name': 'epel', 
                 'url':'http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-3.noarch.rpm'},
                {'name': 'elff',
                 'url': 'http://download.elff.bravenet.com/5/i386/elff-release-5-3.noarch.rpm'}]
CHEF_CLIENT_PACKAGES = ['chef',]
CHEF_SERVER_PACKAGES = ['chef-server-api']
CHEF_CLIENT_SERVICES = ['chef-client']
CHEF_SERVER_SERVICES = ['couchdb', 'rabbitmq-server', 'chef-solr', 'chef-solr-indexer', 'chef-server']


def check_version(dist, min):
    version = tuple(dist[1].split('.'))
    if version < min:
        raise RuntimeError('%s version %s < %s' % (dist[0], version, min))


# install repo list
def install_repo(url):
    # already installed ?
    package = url.rsplit('/', 1)[1]
    package_name = package.split('.', 1)[0]
    args = ['rpm', '-qa']
    installed = execute(args, stdout=subprocess.PIPE)[0].split()
    if package_name in installed:
        return
    args = ['rpm', '-Uvh', url]
    execute(args)


def install_chef(opts, args):
    install_chef_client(opts, args)
    if opts.server:
        install_chef_server(opts, args)


def install_chef_client(opts, args):
    args = ['yum', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    execute(args)
    
    # Set name explicitly
    if opts.name:
        path = '/etc/sysconfig/chef-client'
        backup = '%s.%d' % (path, int(time.time()))
        shutil.copy(path, backup)
        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        for i in xrange(len(lines)):
            if lines[i].find('OPTIONS') != -1:
                lines[i] = "OPTIONS=\"-N %s\"\n" % opts.name
        f = open(path, 'w')
        f.writelines(lines)
        f.close()
    start_services(CHEF_CLIENT_SERVICES)


def install_chef_server(opts, args):
    args = ['yum', '-y', 'install']
    args.extend(CHEF_SERVER_PACKAGES)
    execute(args)
    start_services(CHEF_SERVER_SERVICES)

def start_services(services):
    for svc in services:
        args = ['/sbin/service', svc, 'start']
        execute(args)
        args = ['/sbin/chkconfig', svc, 'on']
        execute(args)

        
