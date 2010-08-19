r"""Common functions shared by linux distributions, including installing 
rubygems and bootstrapping a chef rubygems installation
"""

import urllib, tarfile, tempfile, os, os.path, subprocess

import util

RUBYGEMS_SOURCE = 'http://production.cf.rubygems.org/rubygems/rubygems-1.3.7.tgz'
BOOTSTRAP_SOURCE = 'http://s3.amazonaws.com/chef-solo/bootstrap-latest.tar.gz'
CHEF_SOLO_CONFIG = """
file_cache_path "%s"
cookbook_path "%s"
"""
# The bootstrap cookbook ignores chef:path, so the install path will be /srv/chef
CHEF_CLIENT_JSON = """
{
  "chef": {
    "server_url": "%s",
    "init_style": "init"
  },
  "run_list": [ "recipe[chef::bootstrap_client]" ]
}
"""
CHEF_SERVER_JSON = """
{
  "chef": {
    "server_url": "%s",
    "init_style": "init",
    "webui_enabled": "%s"
  },
  "run_list": [ "recipe[chef::bootstrap_server]" ]
}
"""
# FIXME: rhels don't have runit, but debians do

def check_version(dist, min):
    r"""check a distribution version meets a minimum requirement"""
    version = tuple(dist[1].split('.'))
    if version < min:
        raise RuntimeError('%s version %s < %s' % (dist[0], version, min))


def untarball(url):
    r"""Retrieve and extract a tarball"""
    path, header = urllib.urlretrieve(url)
    t = tarfile.open(path, 'r')
    tmppath = tempfile.mkdtemp()
    #t.extractall(tmppath) # not available until 2.5
    for member in t.getmembers():
        t.extract(member, path=tmppath)
    # this assumes that the tarball unpacks nicely into a subdirectory
    extracted = os.path.join(tmppath, os.listdir(tmppath)[0])
    return extracted


def install_rubygems(opts, args):
    r"""Retrieves and installs rubygems from source."""
    # checks if gem is already installed
    try:
        util.execute(['which', 'gem'], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
    except RuntimeError:    
        extracted = untarball(RUBYGEMS_SOURCE)
        util.execute(['ruby','%s/setup.rb' % extracted, '--no-format-executable'])


def gem_install_chef(opts, args):
    
    # checks if chef gem is already installed.
    outs = util.execute(['gem', 'list', '--local'], stdout=subprocess.PIPE)
    for line in outs[0].split('\n'):
        if line.startswith('chef'):
            break
    else:
        util.execute(['gem', 'install', 'chef'])
    

# FIXME: for now we assume that the bootstrap recipe is idempotent
def gem_bootstrap_chef(opts, args):
    r"""Bootstraps chef from a rubygems installation."""
    
    # temporary cookbook cache
    tmppath = tempfile.mkdtemp(prefix='chef-solo')
    
    # chef-solo config
    solo_rb = tempfile.mkstemp(suffix='.rb', prefix='chef-solo')
    os.write(solo_rb[0], CHEF_SOLO_CONFIG % (tmppath, '%s/cookbooks' % tmppath))
    os.close(solo_rb[0])
    
    # chef-client config
    client_json = tempfile.mkstemp(suffix='.json', prefix='chef-client')
    os.write(client_json[0], CHEF_CLIENT_JSON % opts.url)
    os.close(client_json[0])

    util.execute(['chef-solo', '-c', solo_rb[1], 
                  '-j', client_json[1],
                  '-r', BOOTSTRAP_SOURCE])
    
    # chef-server config
    if opts.server:
        if opts.webui:
            webui = 'true'
        else:
            webui = 'false'
        server_json = tempfile.mkstemp(suffix='.json', prefix='chef-server')
        os.write(server_json[0], CHEF_SERVER_JSON % (opts.url, webui))
        os.close(server_json[0])
        
        util.execute(['chef-solo', '-c', solo_rb[1], 
                      '-j', server_json[1],
                      '-r', BOOTSTRAP_SOURCE])
        
    