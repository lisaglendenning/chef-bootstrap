
import os.path, subprocess

from util import *


CHEF_REPOSITORY = 'http://apt.opscode.com/'
CHEF_REPOSITORY_KEY = 'http://apt.opscode.com/packages@opscode.com.gpg.key'
CHEF_CLIENT_PACKAGES = ['chef',]
CHEF_SERVER_PACKAGES = ['chef-server']


def check_version(dist, min):
    version = tuple(dist[1].split('.'))
    if version < min:
        raise RuntimeError('%s version %s < %s' % (dist[0], version, min))


# modify local repo list
def add_repo(repo):
    source = '/etc/apt/sources.list.d/opscode.list'
    if os.path.exists(source):
        return
    f = open(source, 'w')
    f.write('%s\n' % repo)
    f.close()


def install_chef(opts, args):
    install_chef_client(opts, args)
    if opts.server:
        install_chef_server(opts, args)


def install_chef_client(opts, args):
    # Preseed
    execute(['apt-get', '-y', 'install', 'debconf'])
    preseed = [['chef', 'chef/chef_server_url', 'string', opts.url]]
    input = '%s\n' % '\n'.join([' '.join(line) for line in preseed])
    execute(['debconf-set-selections'], input=input)
    
    os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    execute(args)


def install_chef_server(opts, args):
    # preseed settings:
    # chef-solr/amqp_password - password for chef vhost in RabbitMQ.
    # chef-server-webui/admin_password - password for "admin" user in Chef Server WebUI, must be 6 characters.

    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    args.extend(CHEF_SERVER_PACKAGES)
    execute(args)

    