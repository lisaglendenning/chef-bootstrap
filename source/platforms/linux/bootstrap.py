
import platform

def main(argv, system):
    
    # Detect what distribution we're running
    dist = platform.dist()[0].lower()
    try:
        package = __name__.rsplit('.')[0]
        mod = __import__('.'.join([package, dist, 'bootstrap']), 
                         globals(), locals(), 'bootstrap')
        mod.main(argv, system, dist)
    except ImportError:
        raise RuntimeError("Unsupported %s distribution: %s" % (system, dist))
