
import subprocess, urllib, shutil, time, re

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
    'lucid': 'universe',
    'karmic': 'universe',
    'jaunty': 'universe',
    'intrepid': 'universe',
    'hardy': 'universe', 
}
CHEF_CLIENT_PACKAGES = 'rubygems', 'ohai', 'chef',

def get_version(argv):
    args = ['cat', '/etc/issue']
    child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outdata, errdata = child.communicate()
    version = outdata.split()[1]
    version = tuple(version.split('.'))
    return version

def install_repository(argv, version):
    if version < UBUNTU_MIN_VERSION:
        raise RuntimeError('Ubuntu version %s < %s' % (version, UBUNTU_MIN_VERSION))
    
    version_name = UBUNTU_VERSIONS[version]
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
    
def install_chef(argv):
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    subprocess.check_call(args)

#
# The following overrides are temporary (hopefully)
#

# Until 0.8 packages are released, we will only use the testing packages
# and only for karmic+
UBUNTU_MIN_VERSION = ('9', '10')
CHEF_REPOSITORY = 'ppa:jtimberman/opschef'
CHEF_CLIENT_PACKAGES = ['chef',]

def install_repository(argv, version):
    if version < UBUNTU_MIN_VERSION:
        raise RuntimeError('Ubuntu version %s < %s' % (version, UBUNTU_MIN_VERSION))
    
    args = ['add-apt-repository', CHEF_REPOSITORY]
    subprocess.check_call(args)

    # update packages
    args = ['apt-get', 'update']
    subprocess.check_call(args)
    
def install_chef(argv):
    args = ['apt-get', '-y', 'install']
    args.extend(CHEF_CLIENT_PACKAGES)
    subprocess.check_call(args)
    
def main(argv):
    version = get_version(argv)
    install_repository(argv, version)
    install_chef(argv)
    