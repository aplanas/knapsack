import os.path
import re

from remove_package_version import remove_version_or_discard


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

