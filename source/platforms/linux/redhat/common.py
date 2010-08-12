
import subprocess, shutil, time, os, os.path

from util import execute
from platforms.linux.common import *


FEDORA_RELEASES = [ 
    ('14', 'Laughlin'),
    ('13', 'Goddard'),
    ('12', 'Constantine'),
    ('11', 'Leonidas'),
    ('10', 'Cambridge'),
    ('9', 'Sulphur'),
    ('8', 'Werewolf'),
    ('7', 'Moonshine'),
    ('6', 'Zod'),
    ('5', 'Bordeaux'),
    ('4', 'Stentz'),
    ('3', 'Heidelberg'),
    ('2', 'Tettnang'),
    ('1', 'Yarrow')]

REPOSITORIES = [{'name': 'epel', 
                 'url':'http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-3.noarch.rpm'},
                {'name': 'elff',
                 'url': 'http://download.elff.bravenet.com/5/i386/elff-release-5-3.noarch.rpm'}]
CHEF_CLIENT_PACKAGES = ['chef',]
CHEF_SERVER_PACKAGES = ['chef-server-api']
CHEF_CLIENT_SERVICES = ['chef-client']
CHEF_SERVER_SERVICES = ['couchdb', 'rabbitmq-server', 'chef-solr', 'chef-solr-indexer', 'chef-server']

GEM_DEV_TOOLS = ['ruby', 'ruby-shadow', 'ruby-ri', 'ruby-rdoc', 'gcc', 'gcc-c++', 'ruby-devel', 'make']


def yum_install(packages, options=['-y']):
    r"""Takes a list of packages, and optional list of options and installs them using yum."""
    args = ['yum']
    args.extend(options)
    args.append('install')
    args.extend(packages)
    execute(args)


def check_fedora(opts, args):
    return (opts.dist[1], opts.dist[2]) in FEDORA_RELEASES


def install_remote_rpm(url):
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
    yum_install(CHEF_CLIENT_PACKAGES)
    
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
    yum_install(CHEF_SERVER_PACKAGES)
    start_services(CHEF_SERVER_SERVICES)
    if opts.webui:
        yum_install(['chef-server-webui'])
        start_services(['chef-server-webui'])


def start_services(services):
    for svc in services:
        args = ['/sbin/service', svc, 'start']
        execute(args)
        args = ['/sbin/chkconfig', svc, 'on']
        execute(args)


def gem_install_chef(opts, args):
    r"""Installs chef through a rubygems installation."""
    # TODO: Gem installation should probably be in opts and merged with install_chef  
    yum_install(GEM_DEV_TOOLS)
    install_rubygems(opts, args)
    bootstrap_chef(opts, args)
    
    # post bootstrap steps for RHEL derivatives.
    # FIXME: this needs to be more parameterized and suck less
    GEMDIR = "/usr/lib/ruby/gems/1.8/gems/chef-0.9.8"
    
    # FIXME: getent outputs nothing but apparently returns 2, causing python to get mad.
    # A different way of detecting whether the user exists might be necessary.
    """ 
    outs = execute(['getent', 'passwd', 'chef'],
                   stdout=subprocess.PIPE)
    if not outs[0]:
        execute(['/usr/sbin/useradd', 'chef'])
    """
    # This works for now.
    try:
        execute(['/usr/sbin/useradd', 'chef'])
    except RuntimeError:
        print "chef user already exists"
        
    execute(['chown', 'chef:chef', '-R', '/var/lib/chef'])
    execute(['chown', 'chef:chef', '-R', '/var/log/chef'])
    os.chdir(GEMDIR)
    path = 'distro/redhat/etc/sysconfig'
    for f in os.listdir(path):
        shutil.copy(os.path.join(path, f), '/etc/sysconfig')
    path = 'distro/redhat/etc/init.d'
    for f in os.listdir(path):
        shutil.copy(os.path.join(path, f), '/etc/init.d')
    path = 'distro/common/man/man1'
    for f in os.listdir(path):
        shutil.copy(os.path.join(path, f), '/usr/local/share/man/man1')
    path = 'distro/common/man/man8'
    for f in os.listdir(path):
        shutil.copy(os.path.join(path, f), '/usr/local/share/man/man8')
    execute('chmod +x /etc/init.d/chef-*', shell=True)
    execute(['/sbin/service', 'chef-client', 'start'])

