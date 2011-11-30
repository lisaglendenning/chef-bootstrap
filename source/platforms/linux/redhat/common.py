r"""Common functions and constants for RHEL and derivatives"""

import shutil, os.path, tempfile, stat

from platforms.linux.common import call, fetch, untarball, \
CHEF_VERSION_MIN, BOOTSTRAP_URL, CHEF_SERVER_BOOTSTRAP_TEXT, \
install_source_rubygems, install_gem, bootstrap_chef_solo


FEDORA_RELEASES = [ 
    ('16', 'Verne'),
    ('15', 'Lovelock'),
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

AEGISCO_URL = 'http://rpm.aegisco.com/aegisco/el5/aegisco.repo'
AEGISCO_FILE = '/etc/yum.repos.d/aegisco.repo'
RBEL = {'5': {'name': 'rbel5-release-1.0-2.el5',
              'url': 'http://rbel.frameos.org/rbel5',},
        '6': {'name': '??',
              'url': 'http://rbel.frameos.org/rbel6',},}
RUBY_PACKAGES = ['ruby', 
            'ruby-devel', 
            'ruby-ri', 
            'ruby-rdoc', ] 
# PROBLEM: ruby-shadow package not available from AEGISCO or RBEL5
# soo...not installing it?
SUPPORT_PACKAGES = ['gdbm',
            'gcc', 
            'gcc-c++', 
            'automake',
            'autoconf',
            'make', 
            'curl',
            'dmidecode',]



def check_fedora(opts, args):
    r"""Fedora distributions are sometimes identified as 'redhat' by the 
    platform module. This checks by the version number and codename
    """
    return (opts.dist[1], opts.dist[2]) in FEDORA_RELEASES


def install_remote_rpm(url, name=None):
    r"""Installs an rpm from a url."""
    # already installed ?
    if name is None:
        name = url.rsplit('/', 1)[1]
    args = ['rpm', '-qa']
    err, (stdout, stderr) = call(args, 0, stdout=True)
    if name in stdout.split():
        return
    args = ['rpm', '-Uvh', url]
    call(args, 0)


def install_package(package, opts=('-y',), arch=None):
    r"""Takes a package and optional list of options and installs it using yum."""
    # already installed?
    result = call(('yum', 'list', '-q', 'installed', package))
    if result[0] == 0:
        return
    # check for available architecture 
    if arch is not None:
        for a in (arch, 'noarch'):
            p = '%s.%s' % (package, a)
            result = call(('yum', 'list', '-q', 'available', package))
            if result[0] == 0:
                package = p
                break
        else:
            raise RuntimeError('Unable to find package %s for architecture %s' % (package, arch))
    args = ['yum', 'install']
    args += opts        
    args += (package,)
    call(args, 0)


def install_support(opts, args):
    version = tuple(opts.dist[1].split('.'))

    # Install repositories
    if version[0] == '5':
        # needed for Ruby 1.8.7
        fetch(AEGISCO_URL, AEGISCO_FILE, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IWUSR)
    if version[0] > '5' or opts.server:
        rbel = RBEL[version[0]]
        install_remote_rpm(rbel['url'], rbel['name'])
    
    # Install support packages
    for pkg in SUPPORT_PACKAGES:
        install_package(pkg, arch=opts.arch)
    if version[0] == '5':
        ruby_repo = 'aegisco'
    else:
        ruby_repo = 'rbel6'
    for pkg in RUBY_PACKAGES:
        install_package(pkg, ('-y', '--disablerepo=*', '--enablerepo=%s' % ruby_repo), arch=opts.arch)

    install_source_rubygems()


# 11/28/2011 WORKAROUND: for issue COOK-528
def bootstrap_chef_server(opts, args):
    tmpcache, tmpconf = bootstrap_chef_solo()
    
    # temporary attribute file
    tmpattr = tempfile.mkstemp(suffix='.json', prefix='chef')
    attrs = {}
    attrs['server'] = opts.url
    if opts.webui:
        attrs['webui'] = 'true'
    else:
        attrs['webui'] = 'false'
    if opts.dist[0] in ('redhat', 'fedora'):
        attrs['init'] = 'init'
    else:
        attrs['init'] = 'runit'
    content = CHEF_SERVER_BOOTSTRAP_TEXT % attrs
    os.write(tmpattr[0], content)
    os.close(tmpattr[0])
    
    # WORKAROUND
    untarball(BOOTSTRAP_URL, tmpcache)
    source = os.path.join(os.path.dirname(__file__), 'gecode.rb')
    dest = '%s/cookbooks/gecode/recipes/default.rb' % tmpcache
    os.rename(dest, '%s.orig' % dest)
    shutil.copy(source, dest)
    
    # execute bootstrap
    args = ['chef-solo', '-c', tmpconf, '-j', tmpattr[1]]
    call(args, 0)


def install_chef(opts, args):
    install_gem('chef', CHEF_VERSION_MIN)
    if opts.server:
        bootstrap_chef_server(opts, args)
