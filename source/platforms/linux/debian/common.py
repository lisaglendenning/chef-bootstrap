
import os.path, subprocess, urllib

from util import execute


CHEF_REPOSITORY = 'http://apt.opscode.com/'
CHEF_REPOSITORY_KEY = 'http://apt.opscode.com/packages@opscode.com.gpg.key'
CHEF_CLIENT_PACKAGES = ['chef',]
CHEF_SERVER_PACKAGES = ['chef-server', 'chef-server-api'] 

def apt_install(packages, options=[]):
    r"""Takes a list of packages, and optional list of options and installs them using apt-get."""
    args = ['apt-get', '-y'].extend(options)
    args.append('install')
    args.extend(packages)
    execute(args)

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
    apt_install(['debconf'])
    preseed = [['chef', 'chef/chef_server_url', 'string', opts.url]]
    input = '%s\n' % '\n'.join([' '.join(line) for line in preseed])
    execute(['debconf-set-selections'], input=input)
    
    os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
    apt_install(CHEF_CLIENT_PACKAGES)

# one of chef-server and chef-server-api is installed depending on whether webui is to be run
def install_chef_server(opts, args):
    # preseed settings:
    # chef-solr/amqp_password - password for chef vhost in RabbitMQ.
    # chef-server-webui/admin_password - password for "admin" user in Chef Server WebUI, must be 6 characters.
    
    if opts.webui:
        server_packages = [CHEF_SERVER_PACKAGES[0]]
    else:
        server_packages = [CHEF_SERVER_PACKAGES[1]]
    
    apt_install(server_packages)


def add_key(key_url):
    keyfile = urllib.urlretrieve(key_url)
    # was keyfile, headers = ..., headers is unused?
    args = ['apt-key', 'add', keyfile]
    execute(args)


def apt_update():
    # update packages
    args = ['apt-get', 'update']
    execute(args)

