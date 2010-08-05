
RUBYGEMS_SOURCE = 'http://production.cf.rubygems.org/rubygems/rubygems-1.3.7.tgz'

def check_version(dist, min):
    version = tuple(dist[1].split('.'))
    if version < min:
        raise RuntimeError('%s version %s < %s' % (dist[0], version, min))
