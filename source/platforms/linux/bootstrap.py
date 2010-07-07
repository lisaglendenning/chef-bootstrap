
import platform

def main(argv, system):
    
    # Detect what distribution we're running
    dist = platform.dist()
    try:
        package = __name__.rsplit('.', 1)[0]
        modname = dist[0].lower()
        mod = __import__('.'.join([package, modname, 'bootstrap']), 
                         globals(), locals(), 'bootstrap')
        mod.main(argv, system, dist)
    except ImportError:
        raise RuntimeError("Unsupported %s distribution: %s" % (system, dist))
