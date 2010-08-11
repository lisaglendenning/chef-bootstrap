
import subprocess, shutil, time

from util import execute

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


def yum_install(packages, options=[]):
    r"""Takes a list of packages, and optional list of options and installs them using yum."""
    args = ['yum', '-y']
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

