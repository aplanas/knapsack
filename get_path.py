#!/usr/bin/python
# -*- coding: utf-8 -*-

# Parse the Apache log life and extract the PATH field

import argparse
import os.path
import re
import sys


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
PACKAGE = re.compile(r'(.+)-[^-]+-[^-]+\.(\w+)\.(?:d?)rpm') # Adapted from 'xmath'
BOTS = re.compile(r'<String>(.*?)</String>')


def parse_file(infile, outfile, bots):
    """Parse the file and print the PATH for every line."""
    for line in infile:
        m = PATTERN.match(line)
        hit = m.groupdict() if m else None
        if not hit:
            continue

        # Normalize the path
        path = os.path.normpath(hit['path'])

        # If it is not any importan file, ignore the entry
        if not path.endswith(('.rpm', '.drpm', '.iso', '.xml.gz')):
            continue

        if hit['user_agent'] in bots:
            continue

        # Get the path without the version
        m = PACKAGE.match(path)
        path = m.groups()[0] if m else path

        print >> outfile, hit['ip'], path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse software.o.o downloads information and get the PATH field.')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='Logfiles used to read the information')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    bots = set(l.strip() for l in open('bots.txt'))
    parse_file(args.infile, args.outfile, bots)
