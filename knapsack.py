#!/usr/bin/python
# -*- coding: utf-8 -*-

# Implementatio of the 0/1 knapsack problem (0/1 KP)
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


__author__ = 'Alberto Planas <aplanas@suse.de>'

import argparse


# Byte -> Mega
B_M = 1024 * 1024
# Kilo -> Mega
K_M = 1024


def kpsolution(weights, capacity, keep):
    """Reconstruct the solution using the keep matrix."""
    solution = []

    # We go from (n, W) backtracking according to the keep matrix
    j = capacity

    for i in range(len(weights), 0, -1):
        print i, j
        if keep[i][j]:
            solution.append(i-1)
            j = j - weights[i-1]

    solution.reverse()
    return solution
    

def knapsack(values, weights, capacity):
    """Implement the 0/1 knapsack solver."""

    # We use the dynamic programming pseudo-polynomial time algorithm

    # Initialize the matrix
    m = [[0] * (capacity+1) for _ in range(len(values)+1)]
    keep = [[0] * (capacity+1) for _ in range(len(values)+1)]

    # Build the rest of the table. In every iteration m[i][j] will
    # store the maximum value that we can carry using a combination of
    # items of {1, ..., i}, with weight at most of j.
    for i in range(1, len(weights)+1):
        for j in range(capacity+1):
            # If the weight of the i item is bigger than the limit j,
            # we can't carry it.
            if weights[i-1] > j:
                m[i][j] = m[i-1][j]
            else:
                # Get the maximum value when we leave or we carry the
                # i item.
                #
                # m[i-1][j]: maximun value if we don't take the item
                #
                # m[i-1][j-weight[i]] + values[i]: if we the item, the
                #   new value is the value of the item plus the
                #   maximum value when wehave enough room for this
                #   item.
                #
                m[i][j] = max(m[i-1][j], m[i-1][j-weights[i-1]] + values[i-1])
                if m[i][j] != m[i-1][j]:
                    keep[i][j] = 1

    return kpsolution(weights, capacity, keep)



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
                if path.starswith('.'):
                    path = path[1:]
            if path:
                item_list.append((int(size) / ratio, path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resolve the knapsack problem with hierarchical relations.')
    parser.add_argument('--price', help='Price sorted file')
    parser.add_argument('--size', help='Size sorted file')
    parser.add_argument('--wsize', type=int, help='Knapsack max size in MB')

    args = parser.parse_args()

    prices = read_file(args.price)
    sizes = read_file(args.size, ratio=K_M, remove_dot=True)

    print knapsack([10, 40, 30, 50], [5, 4, 6, 3], 10)
