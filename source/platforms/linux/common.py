r"""Common functions shared by linux distributions, including installing 
rubygems and bootstrapping a chef rubygems installation
"""

import urllib, tarfile, tempfile, os, os.path, subprocess, shutil, time, stat

CHEF_VERSION_MIN = '0.10.4'

RUBYGEMS_VERSION = '1.8.10'
RUBYGEMS_URL = 'http://production.cf.rubygems.org/rubygems/rubygems-%s.tgz' % RUBYGEMS_VERSION
RUBYGEMS_PATH = 'rubygems-%s' % RUBYGEMS_VERSION

BOOTSTRAP_URL = 'http://s3.amazonaws.com/chef-solo/bootstrap-latest.tar.gz'
CHEF_SOLO_BOOTSTRAP_TEXT = """
file_cache_path  '%(path)s'
cookbook_path    '%(path)s/cookbooks'
"""
CHEF_SERVER_BOOTSTRAP_TEXT = """
{
  "chef_server": {
    "server_url": "%(server)s",
    "init_style": "%(init)s",
    "webui_enabled": "%(webui)s"
  },
  "run_list": [ "recipe[chef-server::rubygems-install]" ]
}
"""


def call(args, expected_err=None, stdout=None, stderr=None, input=None, **kwargs):
    r"""Execute a subprocess."""
    for arg, name in ((stdout, 'stdout'), (stderr, 'stderr'), (input, 'stdin')):
        if arg is True:
            kwargs[name] = subprocess.PIPE
    child = subprocess.Popen(args, **kwargs)
    if (stdout, stderr, input) != (None, None, None):
        output = child.communicate(input)
    else:
        output = None
        child.wait()
    result = (child.returncode, output)
    if expected_err is not None:
        if expected_err != child.returncode:
            raise RuntimeError('%s returned %s' % (args, result))
    return result


def check_version(dist, min):
    r"""check a distribution version meets a minimum requirement"""
    version = tuple(dist[1].split('.'))
    if version < min:
        raise RuntimeError('%s version %s < %s' % (dist[0], version, min))


def fetch(url, path=None, mode=None):
    r"""Save a copy of a remote file."""
    file, header = urllib.urlretrieve(url)
    if path is not None:
        shutil.copy(file, path)
        file = path
    if mode is not None:
        os.chmod(file, mode)
    return file


def untarball(url, path=None):
    r"""Retrieve and extract a tarball"""
    fetched = fetch(url)
    t = tarfile.open(fetched, 'r')
    if path is None:
        path = tempfile.mkdtemp()
    #extractall() not available until 2.5
    for member in t.getmembers():
        t.extract(member, path=path)
    return path


def install_source_rubygems():
    r"""Installs rubygems from source."""
    # check installed version
    result = call(('which', 'gem'))
    if result[0] == 0:
        result = call(('gem', '-v'), stdout=True)
        if result[1][0] >= RUBYGEMS_VERSION:
            return
    path = os.path.join(untarball(RUBYGEMS_URL), RUBYGEMS_PATH)
    args = ['ruby', 'setup.rb', '--no-format-executable']
    call(args, 0, cwd=path)


def install_gem(name, version=None):
    result = call(('which', 'gem'))
    if result[0] != 0:
        raise RuntimeError('Missing RubyGems installation')
    result = call(('gem', 'list', '--installed', name))
    # already installed?
    if result[0] == 0:
        if version is None:
            return
        # version check
        args = ['gem', 'list', '--local', '--versions', name]
        result = call(args, stdout=True)
        for line in result[1][0].split('\n'):
            words = line.split()
            if words[0] == name:
                installed = words[1].strip('()')
                if installed >= version:
                    return
                break
    args = ['gem', 'install', name, '--no-ri', '--no-rdoc']
    call(args, 0)


def bootstrap_chef_solo():
    # temporary cache for bootstrap
    tmpcache = tempfile.mkdtemp(prefix='chef-solo')
    
    # temporary configure file
    tmpconf = tempfile.mkstemp(suffix='.rb', prefix='chef-solo')
    content = CHEF_SOLO_BOOTSTRAP_TEXT % {'path': tmpcache}
    os.write(tmpconf[0], content)
    os.close(tmpconf[0])
    
    return tmpcache, tmpconf[1]


# TODO: for now we assume that the bootstrap recipe is idempotent
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
    
    # execute bootstrap
    args = ['chef-solo', '-c', tmpconf, '-j', tmpattr[1], '-r', BOOTSTRAP_URL]
    call(args, 0)
