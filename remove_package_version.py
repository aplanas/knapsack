#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse

from get_path import PACKAGE
from knapsack import read_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Group files in directories and add the size.')
    parser.add_argument('file', help='File to remove the version name')

    args = parser.parse_args()

    items = read_file(args.file)

    items_group = {}
    for value, path in items:
        if not path.startswith('/'):
            path = '/' + path
        m = PACKAGE.match(path)
        path = m.groups()[0] if m else path
        old_value = items_group.get(path, 0)
        items_group[path] = old_value + value

    for path, size in items_group.iteritems():
        print size, path
