
import subprocess, re

from platforms.linux2 import *

def main(argv):
    
    # Determine what distribution we're running
    args = ['cat', '/etc/issue']
    child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outdata, errdata = child.communicate()
    for dist in distributions:
        if re.search(dist, outdata, re.IGNORECASE):
            mod = __import__('.'.join([__package__, dist, 'bootstrap']), 
                                      fromlist='bootstrap')
            mod.main(argv)
            break
