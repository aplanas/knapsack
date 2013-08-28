#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import re

from knapsack import read_file

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Group files in directories and add the size.')
    parser.add_argument('file', help='File to remove the version name')

    args = parser.parse_args()

    items = read_file(args.file, laplacian=False)

    items_group = {}
    for value, path in items:
        path = remove_version_or_discard(path)
        if path:
            old_value = items_group.get(path, 0)
            items_group[path] = old_value + value

    for path, size in items_group.iteritems():
        print size, path
