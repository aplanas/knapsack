#!/usr/bin/python
# -*- coding: utf-8 -*-

# Group different filenames path and calculate directory sizes.

import argparse

from groups import treefy
from knapsack import read_file


def calc_size(node):
    if 'value' in node.attr:
        return node.attr['value']
    node.attr['value'] = sum(calc_size(n) for n in node.itervalues())
    return node.attr['value']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Group files in directories and add the size.')
    parser.add_argument('--size', help='Size sorted file')

    args = parser.parse_args()

    sizes_tree = treefy(read_file(args.size))

    calc_size(sizes_tree)
    sizes_tree.print_tree()
