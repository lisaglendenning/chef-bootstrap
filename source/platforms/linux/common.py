
import urllib, tarfile, tempfile, os, os.path

import util

#
# Rubygems install
#

RUBYGEMS_SOURCE = 'http://production.cf.rubygems.org/rubygems/rubygems-1.3.7.tgz'
BOOTSTRAP_SOURCE = 'http://s3.amazonaws.com/chef-solo/bootstrap-latest.tar.gz'
CHEF_SOLO_CONFIG = """
file_cache_path "/tmp/chef-solo"
cookbook_path "/tmp/chef-solo/cookbooks"
"""
CHEF_CLIENT_JSON = """
{
  "chef": {
    "server_url": "%s"
  },
  "run_list": [ "recipe[chef::bootstrap_client]" ]
}
"""


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
    extracted = untarball(RUBYGEMS_SOURCE)
    util.execute(['ruby','%s/setup.rb' % extracted, '--no-format-executable'])
    util.execute(['gem', 'install', 'chef'])


# TODO: add functions to bootstrap server/webui also
def bootstrap_chef(opts, args):
    r"""Bootstraps chef from a rubygems installation."""
    
    # chef-solo config
    solo_rb = tempfile.NamedTemporaryFile(suffix='.rb', prefix='chef-solo')
    solo_rb.write(CHEF_SOLO_CONFIG)
    solo_rb.close()
    
    # chef-client config
    client_json = tempfile.NamedTemporaryFile(suffix='.json', prefix='chef-client')
    client_json.write(CHEF_CLIENT_JSON % opts.url)
    client_json.close()
    
    util.execute(['chef-solo', '-c', solo_rb.name, 
                  '-j', client_json.name,
                  '-r', BOOTSTRAP_SOURCE])
    