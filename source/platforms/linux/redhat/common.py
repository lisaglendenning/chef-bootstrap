r"""Common functions and constants for RHEL and derivatives"""

import subprocess, shutil, time, os, os.path

import util
import platforms.linux.common


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
                 'url':'http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-4.noarch.rpm'},
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
    util.execute(args)


def check_fedora(opts, args):
    r"""Fedora distributions are sometimes identified as 'redhat' by the 
    platform module. This checks by the version number and codename
    """
    return (opts.dist[1], opts.dist[2]) in FEDORA_RELEASES


def install_remote_rpm(url):
    r"""Installs an rpm from a url."""
    # already installed ?
    package = url.rsplit('/', 1)[1]
    package_name = package.split('.', 1)[0]
    args = ['rpm', '-qa']
    installed = util.execute(args, stdout=subprocess.PIPE)[0].split()
    if package_name in installed:
        return
    args = ['rpm', '-Uvh', url]
    util.execute(args)


def install_chef(opts, args):
    install_chef_client(opts, args)
    if opts.server:
        install_chef_server(opts, args)


def install_chef_client(opts, args):
    r"""installs a chef client with RPMs"""
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
    
    # Bootstrap parameters
    if opts.validation or opts.url:
        path = '/etc/chef/client.rb'
        backup = '%s.%d' % (path, int(time.time()))
        shutil.copy(path, backup)
        f = open(path, 'r')
        lines = f.readlines()
        f.close()
        for i in xrange(len(lines)):
            if opts.validation:
                if lines[i].find('validation_key') != -1:
                    lines[i] = "validation_key \t\"%s\"\n" % opts.validation
            if opts.url:
                if lines[i].find('chef_server_url') != -1:
                    lines[i] = "chef_server_url \t\"%s\"\n" % opts.url
        f = open(path, 'w')
        f.writelines(lines)
        f.close()
    
    start_services(CHEF_CLIENT_SERVICES)


def install_chef_server(opts, args):
    r"""installs a chef server with RPMs"""
    yum_install(CHEF_SERVER_PACKAGES)
    start_services(CHEF_SERVER_SERVICES)
    if opts.webui:
        yum_install(['chef-server-webui'])
        start_services(['chef-server-webui'])


def start_services(services):
    r"""starts services given in a list"""
    for svc in services:
        args = ['/sbin/service', svc, 'status']
        try:
            util.execute(args)
        except RuntimeError:
            args = ['/sbin/service', svc, 'start']
            util.execute(args)
        args = ['/sbin/chkconfig', svc, 'on']
        util.execute(args)


def gem_install_chef(opts, args):
    r"""Installs chef through a rubygems installation."""
    # TODO: Gem installation should probably be in opts and merged with install_chef  
    yum_install(GEM_DEV_TOOLS)
    platforms.linux.common.install_rubygems(opts, args)
    platforms.linux.common.gem_install_chef(opts, args)
    platforms.linux.common.gem_bootstrap_chef(opts, args)
    
    # post bootstrap steps for RHEL derivatives.
    # FIXME: this needs to be more parameterized
    
    # FIXME: This is a quick fix to a previous chef user check, might need improvement
#    try:
#        util.execute(['/usr/sbin/useradd', 'chef'])
#    except RuntimeError:
#        print "/usr/sbin/useradd chef failed, assuming user exists"
    try:
        util.execute(['getent', 'passwd', 'chef'])
    except RuntimeError:
        util.execute(['/usr/sbin/useradd', 'chef'])
        
    util.execute(['chown', '-R', 'chef:chef', '/srv/chef'])
    
    # FIXME: this will break with other version of chef or gems
    GEMDIR = "/usr/lib/ruby/gems/1.8/gems/chef-0.9.8"
    COPY_INFO = [('distro/redhat/etc/', '/etc/', ['sysconfig','init.d']),
                 ('distro/common/man/', '/usr/local/share/man/', ['man1','man8'])]
    os.chdir(GEMDIR)
    for source_base, target_base, directories in COPY_INFO:
        for dir in directories:
            source = source_base + dir
            target = target_base + dir
            for f in os.listdir(source):
                shutil.copy(os.path.join(source, f), target)
    util.execute('chmod +x /etc/init.d/chef-*', shell=True)
    
    services = CHEF_CLIENT_SERVICES
    if opts.server:
        # Server services need to be added to chkconfig in addition to being started
        # Note: untested
        server_services = ['chef-server','chef-solr', 'chef-solr-indexer']
        if opts.webui:
            server_services.append('chef-server-webui')
        for svc in server_services:
            args = ['/sbin/chkconfig', '--add', svc]
            util.execute(args)
        services.extend(server_services)
    start_services(services)


