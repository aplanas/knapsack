#
# Utility functions
#

import os.path
import re


def read_file(filename, ratio=1, laplacian=True, as_int=True, remove_dot=False, with_time=False):
    """Read a file in the format <NUM> <PATH>."""
    item_list = []

    def _item(size, _time=None, path=None):
        if _time:
            return (size, tuple(int(t) for t in _time.split('-')), path)
        return (size, path)

    with open(filename) as f:
        for line in f:
            fields = line.split()
            
            if not with_time:
                size, path = fields[0], ' '.join(fields[1:])
                _time = None
            else:
                size, _time, path = fields[0], fields[1], ' '.join(fields[2:])

            if remove_dot:
                if path.startswith('.'):
                    path = path[1:]
            if path:
                # The +1 is some kind of laplacian smoothing aproximation.
                l = 1 if laplacian else 0
                l = 0
                # When coputing the KP is better to use int, and float
                # when groping.
                s = int(size) if as_int else float(size)
                item_list.append(_item(l+s/ratio, _time, path))

    return item_list


# Different parts of a log line
PARTS = [
    r'(?P<ip>\S+)',                     # host %h
    r'\S+',                             # indent %l (unused)
    r'\S+',                             # user %u
    r'\[(?P<date>.+)\]',                # time %t
    r'"(?:GET|HEAD) (?P<path>[^ ]+)[^"]*"',  # request "%r"
    r'(?P<status>\d+)',                 # status %>s
    r'(?P<size>\S+)',                   # size %b (careful, can be '-')
    r'"(?P<referrer>[^"]*)"',           # referer "%{Referer}i"
    r'"(?P<user_agent>(?:[^\\"]|\\.)*)"',    # user agent "%{User-agent}i"
    r'(?P<rest>.*)',
]
PATTERN = re.compile(r'\s+'.join(PARTS)+r'\s*$')
BOTS = re.compile(r'<String>(.*?)</String>')


def parse_file(infile, outfile, bots):
    """Parse the file and print the PATH for every line."""
    for line in infile:
        m = PATTERN.match(line)
        hit = m.groupdict() if m else None
        if not hit or hit['status'] == '404' or hit['user_agent'] in bots:
            continue

        # Normalize the path
        path = os.path.normpath(hit['path'])

        # If it is not any importan file, ignore the entry
        if not path.endswith(('.rpm', '.drpm', '.iso', '.xml.gz')):
            continue

        # Get the path without the version
        path = remove_version_or_discard(path)
        if path:
            print >> outfile, hit['ip'], path



PACKAGE = re.compile(r'(.+)-[^-]+-[^-]+\.(\w+)\.(?:d?)rpm') # Adapted from 'xmath'
HEX64 = re.compile(r'[0-9a-f]{64}')


def remove_version_or_discard(path):
    """Remove the version of None if is not versioned."""
    # Get the path without the version
    m = PACKAGE.match(path)
    _path = m.groups()[0] if m else path

    # If have an HEX64 number, remove it
    _path = HEX64.sub('', _path)

    # Discard the file if is a non-versioned small XML file
    _path = _path if _path != path or not path.endswith('.xml.gz') else None

    return _path
