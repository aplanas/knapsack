#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

from knapsack import read_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge payloads files')
    parser.add_argument('payloads', metavar='FILE', nargs='+',
                        help='Price sorted file')

    args = parser.parse_args()

    prices = {p[1]: p[0] for p in read_file(args.payloads[0])}
    for price_file in args.payloads[1:]:
        for hits, path in read_file(price_file):
            hits = hits + prices.get(path, 0)
            prices[path] = hits

    for path, hits in prices.iteritems():
        print hits, path
