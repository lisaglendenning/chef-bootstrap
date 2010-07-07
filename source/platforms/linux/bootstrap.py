
import platform

def main(argv, system):
    
    # Detect what distribution we're running
    dist = platform.dist()[0].lower()
    try:
        mod = __import__('.'.join([__name__, dist, 'bootstrap']), 
                         globals(), locals(), 'bootstrap')
        mod.main(argv, system, dist)
    except ImportError:
        raise RuntimeError("Unsupported %s distribution: %s" % (system, dist))
