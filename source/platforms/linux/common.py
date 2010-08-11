
import urllib, tarfile, tempfile, os, os.path, subprocess

import util

#
# Rubygems install
#

RUBYGEMS_SOURCE = 'http://production.cf.rubygems.org/rubygems/rubygems-1.3.7.tgz'
BOOTSTRAP_SOURCE = 'http://s3.amazonaws.com/chef-solo/bootstrap-latest.tar.gz'
CHEF_SOLO_CONFIG = """
file_cache_path "%s"
cookbook_path "%s"
"""
CHEF_CLIENT_JSON = """
{
  "chef": {
    "server_url": "%s",
    "init_style": "init"
  },
  "run_list": [ "recipe[chef::bootstrap_client]" ]
}
"""
# FIXME: rhels don't have runit, but debians do

def check_version(dist, min):
    version = tuple(dist[1].split('.'))
    if version < min:
        raise RuntimeError('%s version %s < %s' % (dist[0], version, min))


def untarball(url):
    path, header = urllib.urlretrieve(url)
    t = tarfile.open(path, 'r')
    tmppath = tempfile.mkdtemp()
    t.extractall(tmppath)
    # this assumes that the tarball unpacks nicely into a subdirectory
    extracted = os.path.join(tmppath, os.listdir(tmppath)[0])
    return extracted


def install_rubygems(opts, args):
    r"""Retrieves and installs rubygems from source."""
    try:
        util.execute(['gem', '--help'], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
    except RuntimeError:    
        extracted = untarball(RUBYGEMS_SOURCE)
        util.execute(['ruby','%s/setup.rb' % extracted, '--no-format-executable'])
    
    outs = util.execute(['gem', 'list', '--local'], stdout=subprocess.PIPE)
    for line in outs[0].split('\n'):
        if line.startswith('chef'):
            break
    else:
        util.execute(['gem', 'install', 'chef'])


# TODO: add functions to bootstrap server/webui also
def bootstrap_chef(opts, args):
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
    