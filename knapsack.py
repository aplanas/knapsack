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
import sys

from knapsacklib import knapsack


# Byte -> Mega
B_M = 1024 * 1024
# Kilo -> Mega
# K_M = 1024


PRICE_CUTOFF = 50  # Hits
SIZE_CUTOFF = 0    # Mega
SIZE_CUTOFF_GREEDY = 2048  # Byte 


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resolve the knapsack problem.')
    parser.add_argument('--price', help='Price sorted file')
    parser.add_argument('--size', help='Size sorted file')
    parser.add_argument('--wsize', type=int, help='Knapsack max size in MB')
    parser.add_argument('--fixsize', action='store_true',
                        help='Use a lineal model to calculate the correct size')
    parser.add_argument('--slope', type=float, default=1.10873,
                        help='Slope of the lineal model used to fix the size')
    parser.add_argument('--intercept', type=float, default=17467.82762,
                        help='Intercept of the lineal model used to fix the size')

    args = parser.parse_args()

    if args.fixsize:
        args.wsize = (args.wsize - args.intercept) / args.slope - 1024
        print >> sys.stderr, 'Fixed the size of the KP to {0}MB ({1}GB)'.format(
            args.wsize, args.wsize/1024)

    print >> sys.stderr, 'Reading size list and converting size into MB...'
    sizes = {s[1]: s[0] for s in read_file(args.size, ratio=B_M) if s[0] >= SIZE_CUTOFF}
    sizes_set = set(sizes.iterkeys())
    print >> sys.stderr, 'Reading price list...'
    prices = {p[1]: p[0] for p in read_file(args.price)
              if p[0] >= PRICE_CUTOFF and p[1] in sizes_set}

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

    print >> sys.stderr, 'Computing 0-1 KP...'
    indexes= knapsack(ordered_prices, ordered_sizes, args.wsize)

    # The KP is done, but if we are far from the KP size (usually
    # because the current KP cover all the real avaliable value), we
    # can switch to a greedy algorithm, adding the bigger retail.
    kp_size = sum(ordered_sizes[i] for i in indexes)

    if kp_size < args.wsize:
        print >> sys.stderr, 'Computing greedy retail (%s < %s)...'%(kp_size, args.wsize)
        sizes_greedy = {s[1]: s[0] for s in read_file(args.size) if s[0] >= SIZE_CUTOFF_GREEDY}
        sizes_set_greedy = set(sizes_greedy.iterkeys())
        retail = {p[1]: p[0] for p in read_file(args.price)
                  if p[0] < PRICE_CUTOFF and p[1] in sizes_set_greedy}
        candidates = sorted(((sizes_greedy[name], name) for name in retail), reverse=True)

        # Fix units here. Convert from Mega (used in KP) to Byte (greedy)
        kp_size *= B_M
        args.wsize *= B_M

        for c_size, c_name in candidates:
            if (kp_size + c_size) < args.wsize:
                kp_size += c_size
                indexes.append(len(ordered_names))
                ordered_names.append(c_name)
                ordered_sizes.append(c_size / B_M)
                ordered_prices.append(retail[c_name])
                prices[c_name] = retail[c_name]

    # Print KP
    for i in indexes:
        # print ordered_prices[i], ordered_names[i]
        print ordered_names[i]


    total_value = sum(i for i in prices.itervalues())
    total_size = sum(i for i in sizes.itervalues())
    kp_value = sum(ordered_prices[i] for i in indexes)
    kp_size = sum(ordered_sizes[i] for i in indexes)

    print >> sys.stderr, 'Total value: {}'.format(total_value)
    print >> sys.stderr, 'Total size: {}'.format(total_size)
    print >> sys.stderr, 'Knapsack value: {}'.format(kp_value)
    print >> sys.stderr, 'Knapsack size: {}'.format(kp_size)


    # Make a binary search in to find the KP size that get the 99% of
    # the overall value

    # wsize_min = 10 * 1024
    # wsize_max = sum(ordered_sizes[i] for i in range(len(ordered_names)) if ordered_prices[i] > 0)

    # EPSILON = 0.01
    # percentage = 0

    # total_value = sum(i for i in prices.itervalues())
    # total_size = sum(i for i in sizes.itervalues())
    # print 'Total value: {}'.format(total_value)
    # print 'Total size: {}'.format(total_size)

    # print 'Initial range: [{} - {}]'.format(wsize_min, wsize_max)
    # while not (percentage - EPSILON <= 99 <= percentage + EPSILON):
    #     wsize_mid = wsize_min + (wsize_max - wsize_min) / 2
    #     print 'KP-{}'.format(wsize_mid)
    #     indexes= knapsack(ordered_prices, ordered_sizes, wsize_mid)

    #     kp_value = sum(ordered_prices[i] for i in indexes)
    #     kp_size = sum(ordered_sizes[i] for i in indexes)
    #     print 'Knapsack value: {} ({})'.format(kp_value, 100.0*kp_value/total_value)
    #     print 'Knapsack size: {} ({})'.format(kp_size, 100.0*kp_size/total_size)

    #     percentage = 100.0 * kp_value / total_value

    #     if percentage < 99:
    #         wsize_min = wsize_mid
    #     else:
    #         wsize_max = wsize_mid
