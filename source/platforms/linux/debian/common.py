
import os.path, tempfile

from util import *


CHEF_REPOSITORY = 'http://apt.opscode.com/'
CHEF_REPOSITORY_KEY = 'http://apt.opscode.com/packages@opscode.com.gpg.key'
CHEF_CLIENT_PACKAGES = ['chef',]
CHEF_SERVER_PACKAGES = ['chef-server'] # doing chef-server doesn't work


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
    # The following settings are available to preseed package installations for non-interactive installations.
    # chef/chef_server_url - the URI for the Chef Server
    # Preseed settings can be specified with debconf-set-selections.
    
    # Preseed
    execute(['apt-get', '-y', 'install', 'debconf'])
    preseed = [['chef', 'chef/chef_server_url', 'string', opts.url]]
    f = tempfile.NamedTemporaryFile(mode='w')
    for answer in preseed:
        f.write('%s\n' % ' '.join(answer))
    args = ['debconf-set-selections', f.name]
    f.close()
    
    os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    execute(args)


def install_chef_server(opts, args):
    # chef-solr/amqp_password - password for chef vhost in RabbitMQ.
    # chef-server-webui/admin_password - password for "admin" user in Chef Server WebUI, must be 6 characters.

    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    args.extend(CHEF_SERVER_PACKAGES)
    execute(args)

    