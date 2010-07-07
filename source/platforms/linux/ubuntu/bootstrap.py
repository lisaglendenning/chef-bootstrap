
import subprocess, urllib, shutil, time, re

UBUNTU_MIN_VERSION = ('8', '04')

CHEF_REPOSITORY = 'http://apt.opscode.com/'
CHEF_REPOSITORY_KEY = 'http://apt.opscode.com/packages@opscode.com.gpg.key'
CHEF_REPOSITORY_COMPONENTS = { 
    'lucid': 'main',
    'karmic': 'main',
    'jaunty': 'main',
    'intrepid': 'main',
    'hardy': 'main', 
}
CHEF_CLIENT_PACKAGES = ['chef',]

def execute(args, **kwargs):
    child = subprocess.Popen(args, **kwargs)
    child.communicate()
    if child.returncode != 0:
        raise RuntimeError("%s: returned %d" % (' '.join(args), child.returncode))

def install_repository(argv, system, dist):
    version = tuple(dist[1].split('.'))
    if version < UBUNTU_MIN_VERSION:
        raise RuntimeError('Ubuntu version %s < %s' % (version, UBUNTU_MIN_VERSION))
    
    # modify local repo list
    repo = ['deb', CHEF_REPOSITORY]
    repo.extend(CHEF_REPOSITORY_COMPONENTS[dist[2]])
    repo = ' '.join(repo)
    source = '/etc/apt/sources.list'
    f = open(source)
    for line in f:
        if re.search(repo, line):
            # assume the repository is already installed
            return
    backup = '/etc/apt/sources.list.%d' % int(time.time())
    shutil.copy(source, backup)
    sources = open(source, 'a')
    sources.write(repo)
    sources.write('\n')
    sources.close()
    
    # add key
    keyfile, headers = urllib.urlretrieve(CHEF_REPOSITORY_KEY)
    args = ['apt-key', 'add', keyfile]
    execute(args)

    # update packages
    args = ['apt-get', 'update']
    execute(args)
    
def install_chef(argv, system, dist):
    # TODO: accept an optional argument as the chef uri
    # The following settings are available to preseed package installations for non-interactive installations.
    # chef/chef_server_url Ð the URI for the Chef Server.
    # chef-solr/amqp_password Ð password for chef vhost in RabbitMQ.
    # chef-server-webui/admin_password Ð password for ÒadminÓ user in Chef Server WebUI, must be 6 characters.
    # Preseed settings can be specified with debconf-set-selections.
    
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    execute(args)

#
# Testing repository information (currently unused)
#
#UBUNTU_MIN_VERSION = ('9', '10')
#CHEF_REPOSITORY = 'ppa:jtimberman/opschef'
#CHEF_CLIENT_PACKAGES = ['chef',]
#
#def install_repository(argv, system, dist):
#    version = tuple(dist[1].split('.'))
#    if version < UBUNTU_MIN_VERSION:
#        raise RuntimeError('Ubuntu version %s < %s' % (version, UBUNTU_MIN_VERSION))
#    
#    args = ['add-apt-repository', CHEF_REPOSITORY]
#    subprocess.check_call(args)
#
#    # update packages
#    args = ['apt-get', 'update']
#    subprocess.check_call(args)
#    
#def install_chef(argv, system, dist):
#    args = ['apt-get', '-y', 'install']
#    args.extend(CHEF_CLIENT_PACKAGES)
#    subprocess.check_call(args)
    
def main(*args):
    install_repository(*args)
    install_chef(*args)
    