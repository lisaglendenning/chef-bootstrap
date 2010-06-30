
import subprocess, urllib, shutil, time, re

CHEF_REPOSITORY = 'http://apt.opscode.com/'
CHEF_REPOSITORY_KEY = 'http://apt.opscode.com/packages@opscode.com.gpg.key'
CHEF_REPOSITORY_ARGS = { 
    '9.1': ('karmic', 'universe'),
    '9.04': ('jaunty', 'universe'),
    '8.10': ('intrepid', 'universe'),
    '8.04': ('hardy', 'universe'), 
}

def install_repository(version):
    # modify local repo list
    repo = ['deb', CHEF_REPOSITORY]
    repo.extend(CHEF_REPOSITORY_ARGS[version])
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
    
    # update apt
    args = ['apt-get', 'update']
    subprocess.check_call(args)


def main(argv):
    
    # Determine what version we're running
    args = ['cat', '/etc/issue']
    child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outdata, errdata = child.communicate()
    version = outdata.split()[1]
    
    install_repository(version)