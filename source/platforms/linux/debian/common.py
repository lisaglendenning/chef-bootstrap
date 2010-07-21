
import shutil, re, time

from util import *


CHEF_REPOSITORY = 'http://apt.opscode.com/'
CHEF_REPOSITORY_KEY = 'http://apt.opscode.com/packages@opscode.com.gpg.key'
CHEF_CLIENT_PACKAGES = ['chef',]
CHEF_SERVER_PACKAGES = ['chef-server',]


def check_version(dist, min):
    version = tuple(dist[1].split('.'))
    if version < min:
        raise RuntimeError('%s version %s < %s' % (dist[0], version, min))


# modify local repo list
def add_repo(repo):
    source = '/etc/apt/sources.list'
    f = open(source)
    for line in f:
        if re.search(repo, line):
            # assume the repository is already installed
            return
    backup = '/etc/apt/sources.list.%d' % int(time.time())
    shutil.copy(source, backup)
    sources = open(source, 'a')
    sources.write('%s\n' % repo)
    sources.close()


def install_chef(opts, args):
    if opts.server:
        install_chef_server(opts, args)
    else:
        install_chef_client(opts, args)


def install_chef_client(opts, args):
    # TODO: accept an optional argument as the chef uri
    # The following settings are available to preseed package installations for non-interactive installations.
    # chef/chef_server_url Ð the URI for the Chef Server.
    # chef-solr/amqp_password Ð password for chef vhost in RabbitMQ.
    # chef-server-webui/admin_password Ð password for ÒadminÓ user in Chef Server WebUI, must be 6 characters.
    # Preseed settings can be specified with debconf-set-selections.
    
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    execute(args)


def install_chef_server(opts, args):
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    execute(args)

    