
import subprocess, urllib, shutil, time, re

# This may be part of the dist tuple ? will have to check
UBUNTU_VERSIONS = {
    ('10','04'): 'lucid',
    ('9','10'): 'karmic',
    ('9','04'): 'jaunty',
    ('8','10'): 'intrepid',
    ('8','04'): 'hardy', 
}

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

def install_repository(argv, system, dist):
    if dist[1] < UBUNTU_MIN_VERSION:
        raise RuntimeError('Ubuntu version %s < %s' % (dist[1], UBUNTU_MIN_VERSION))
    
    version_name = UBUNTU_VERSIONS[dist[1]]
    # modify local repo list
    repo = ['deb', CHEF_REPOSITORY]
    repo.extend(CHEF_REPOSITORY_COMPONENTS[version_name])
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
    subprocess.check_call(args)

    # update packages
    args = ['apt-get', 'update']
    subprocess.check_call(args)
    
def install_chef(argv, system, dist):
    # TODO: accept an optional argument as the chef uri
    # The following settings are available to preseed package installations for non-interactive installations.
    # chef/chef_server_url Ð the URI for the Chef Server.
    # chef-solr/amqp_password Ð password for chef vhost in RabbitMQ.
    # chef-server-webui/admin_password Ð password for ÒadminÓ user in Chef Server WebUI, must be 6 characters.
    # Preseed settings can be specified with debconf-set-selections.
    
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    subprocess.check_call(args)

#
# Testing repository information (currently unused)
#
#UBUNTU_MIN_VERSION = ('9', '10')
#CHEF_REPOSITORY = 'ppa:jtimberman/opschef'
#CHEF_CLIENT_PACKAGES = ['chef',]
#
#def install_repository(argv, system, dist):
#    if dist[1] < UBUNTU_MIN_VERSION:
#        raise RuntimeError('Ubuntu version %s < %s' % (dist[1], UBUNTU_MIN_VERSION))
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
    