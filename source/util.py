
import subprocess, platform

def execute(args, **kwargs):
    child = subprocess.Popen(args, **kwargs)
    outs = child.communicate()
    if child.returncode != 0:
        raise RuntimeError("%s: returned %d" % (' '.join(args), child.returncode))
    return outs

# Detect the OS
def guess_os():
    return platform.system().lower()

# Detect the OS distribution
def guess_dist(os):
    if os == 'linux':
        return platform.dist()
    raise ValueError(os)
