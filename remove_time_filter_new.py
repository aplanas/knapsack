#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

from knapsack import read_file


# Extra points if the path has one of these prefix
PREFIX = ('distribution',
          'update')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Group files in directories and add the size.')
    parser.add_argument('--date', help='Date to filter as a new (YYYY-MM-DD)')
    parser.add_argument('file', help='File to remove the version name')

    args = parser.parse_args()
    args.date = (int(d) for d in args.date.split('-'))

    items = read_file(args.file, laplacian=False, with_time=True)

    for size, _time, path in items:
        print size, path
        if _time >= args.date:
            value = 1000
            value *= 100 if any(path.startswith(p) for p in PREFIX) else 1
            print >> sys.stderr, value, path
