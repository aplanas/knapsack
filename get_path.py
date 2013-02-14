#!/usr/bin/python
# -*- coding: utf-8 -*-

# Parse the Apache log life and extract the PATH field

import argparse
import gzip
import os.path
import re


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


def parse_file(name):
    """Parse the file and print the PATH for every line."""
    with gzip.open(name) as f:
        for line in f:
            m = PATTERN.match(line)
            hit = m.groupdict() if m else None
            if not hit:
                continue

            # Normalize the path
            hit['path'] = os.path.normpath(hit['path'])
            print hit['ip'], hit['path']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse software.o.o downloads information and get the PATH field.')
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='Logfiles used to read the information')
    args = parser.parse_args()

    for name in args.files:
        parse_file(name)
