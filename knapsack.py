#!/usr/bin/python
# -*- coding: utf-8 -*-

# Implementation of the 0/1 knapsack problem (0/1 KP)
#
# (Source Wikipedia: http://en.wikipedia.org/wiki/Knapsack_problem)
#
# Let there be n items, x_1 to x_n there x_i has a value v_i and
# weight w_i. The maximum weight that we can carry in the bag is W.
#
# Objective function:
#  maximize \sum_{i=1}^n v_i x_i subject to \sum_{i=1}^n w_i x_i \leq W
#  where x_i \in {0, 1} and i = 1, ..., n
#


__author__ = ('Alberto Planas <aplanas@suse.de>',
              'Stephan Kulow <coolo@suse.de>')

import argparse

from knapsacklib import knapsack


# Byte -> Mega
B_M = 1024 * 1024
# Kilo -> Mega
K_M = 1024


PRICE_CUTOFF = 100
SIZE_CUTOFF = 1024 / 1024


def read_file(filename, ratio=1, remove_dot=False):
    """Read a file in the format <NUM> <PATH>."""
    item_list = []
    with open(filename) as f:
        for line in f:
            fields = line.split()
            if len(fields) == 2:
                size, path = fields
            else:
                size = fields[0]
                path = ' '.join(fields[1:])
            if remove_dot:
                if path.startswith('.'):
                    path = path[1:]
            if path:
                item_list.append((int(size) / ratio, path))

    return item_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resolve the knapsack problem.')
    parser.add_argument('--price', help='Price sorted file')
    parser.add_argument('--size', help='Size sorted file')
    parser.add_argument('--wsize', type=int, help='Knapsack max size in MB')

    args = parser.parse_args()

    print 'Reading price list...'
    prices = {p[1]: p[0] for p in read_file(args.price) if p[0] >= PRICE_CUTOFF}
    print 'Reading size list...'
    sizes = {s[1]: s[0] for s in read_file(args.size, ratio=K_M) if s[0] >= SIZE_CUTOFF}

    ordered_names = []
    ordered_prices = []
    ordered_sizes = []
    for name, size in sizes.iteritems():
        ordered_names.append(name)
        ordered_sizes.append(size)
        value = 0
        try:
            value = prices[name]
        except:
            pass
        ordered_prices.append(value)

    print 'Computing 0-1 KP...'
    indexes= knapsack(ordered_prices, ordered_sizes, args.wsize)
    for i in indexes:
        print ordered_prices[i], ordered_sizes[i], ordered_names[i]

    # total = sum(p[0] for p in prices)
    # total_kp = sum(prices[i][0] for i in indexes)

    # print knapsack([10, 40, 30, 50], [5, 4, 6, 3], 10)
