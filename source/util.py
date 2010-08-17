r"""General utility functions""" 

import subprocess, platform

def execute(args, input=None, **kwargs):
    r"""Execute a command"""
    if input:
        kwargs['stdin'] = subprocess.PIPE
    child = subprocess.Popen(args, **kwargs)
    outs = child.communicate(input)
    if child.returncode != 0:
        raise RuntimeError("%s: returned %d" % (' '.join(args), child.returncode))
    return outs


def guess_os():
    return platform.system().lower()


def guess_dist(os):
    if os == 'linux':
        return platform.dist()
    raise ValueError(os)
