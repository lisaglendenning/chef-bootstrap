r"""General utility functions""" 

import subprocess, optparse, platform


def configure(argv):
    r"""Parses command-line arguments"""
    parser = optparse.OptionParser()
    parser.add_option("-o", "--os", dest="os", metavar="OS",
                      help="specify one of [linux] to override detection")
    parser.add_option("-d", "--dist", dest="dist", metavar="DIST",
                      help="specify os-specific distribution")
    parser.add_option("-s", "--server", dest="server", action="store_true",
                      default=False, help="install the Chef server")
    parser.add_option("-w", "--webui", dest="webui", action="store_true",
                      default=False, help="install the Chef server webui")
    parser.add_option("-u", "--url", dest="url", metavar="URL",
                      help="specify the Chef server url")
    parser.add_option("-c", "--name", dest="name", metavar="NAME",
                      help="specify the Chef client name")
    parser.add_option("-v", "--validation", dest="validation", metavar="FILE",
                      help="use as the Chef server validation key")
    return parser.parse_args(argv)


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
    r"""Detect the OS"""
    return platform.system().lower()


def guess_dist(os):
    r"""Detect the OS distribution"""
    if os == 'linux':
        return platform.dist()
    raise ValueError(os)
