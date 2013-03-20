#!/usr/bin/python
# -*- coding: utf-8 -*-

# Group different filenames path and try to decide if we can group
# them in a single directory.

import argparse
import sys

from knapsack import B_M, PRICE_CUTOFF, SIZE_CUTOFF, read_file

THRESHOLD = 5000

class TreeNode(dict):
    """Simple generic tree node class."""
    def __init__(self, iterable=(), **attributes):
        self.attr = attributes
        dict.__init__(self, iterable)

    def __repr__(self):
        return '%s(%s, %r)' % (type(self).__name__, dict.__repr__(self), self.attr)

    def create(self, path):
        """Create a new node as indicated by the path."""
        if not path:
            return self

        if not path[0] in self:
            self[path[0]] = TreeNode(name=path[0])
        subtree = self[path[0]]

        return subtree.create(path[1:])

    def count_leaf(self):
        """Count the number of leaf of the tree."""
        result = sum(n.count_leaf() for n in self.itervalues())
        if not result:
            result = 1
        return result

    def get(self, path):
        """Get a node as indicated by the path."""
        assert self.attr['name'] == path[0]

        if len(path) == 1:
            return self

        if not path[1] in self:
            return None
        subtree = self[path[1]]

        return subtree.get(path[1:])

    def is_leaf(self):
        """Return True if is a leaf node."""
        return len(self) == 0

    def is_preleaf(self):
        """Return True if is a pre-leaf node."""
        return len(self) > 0 and all(n.is_leaf() for n in self.itervalues())

    def get_path_preleafs(self):
        """Return a list of node paths where all his children are leafs."""
        if self.is_leaf():
            return []

        if all(n.is_leaf() for n in self.itervalues()):
            return [[self.attr['name']]]

        partial_paths = sum((n.get_path_preleafs() for n in self.itervalues()), [])

        return [[self.attr['name']] + p for p in partial_paths]

    def print_tree(self, rsync=False, path=None):
        path = path or []

        value = self.attr.get('value', 'NOVALUE')
        name = self.attr['name']

        path = path + [name]

        if rsync:
            suff = '/'
            if 'collapse' in self.attr:
                suff = '/***'
            elif self.is_leaf():
                suff = '*'
            str_path = pstr(path)
            if str_path != '/':
                print '+ ' + str_path + suff
        else:
            print value, pstr(path)

        for node in self.itervalues():
            node.print_tree(rsync, path)

    def print_leaf(self, path=None):
        path = path or []

        value = self.attr.get('value', 'NOVALUE')
        name = self.attr['name']

        path = path + [name]

        if self.is_leaf():
            suff = '/' if 'collapse' in self.attr else ''
            print int(value), pstr(path) + suff

        for node in self.itervalues():
            node.print_leaf(path)


def split_path(path):
    """Take a path and split into this components."""
    return [x for x in path.split('/') if x]


def treefy(items):
    """Transform a list of items in a tree."""
    tree = TreeNode(name='/')
    for i, item in enumerate(items):
        value, path = item
        node = tree.create(split_path(path))
        node.attr['value'] = value
    return tree


def pstr(path):
    """Convert a path to a string."""
    pstr = '/'.join(path)[1:]
    return pstr or '/'


def index(tree, sizes, preleaf_path):
    """Calculate the index of the node.

    This index is an ad-hoc solution. Maybe is a good thing to check
    other indexes like Jaccard index (and variations).

    This index is represented by this formulation:

                               Size(preleaf_referenced_files)
    index = ValueOf(preleaf) * ------------------------------
                                Size(preleaf_full_directory)

    Where:

     - ValueOf(preleaf) = Sum of values of the child files.
     - Size(preleaf_referenced_files) = Disk size of the referenced files
     - Size(preleaf_full_directory) = Disk size of the full directory

    """
    value = 0
    partial_size = 0

    preleaf = tree.get(preleaf_path)
    if not preleaf:
        print >> sys.stderr, 'NOT FOUND', pstr(preleaf_path)
        return 0

    for node in preleaf.itervalues():
        value += node.attr['value']
        partial_size += sizes[pstr(preleaf_path + [node.attr['name']])]
    full_size = float(sizes[pstr(preleaf_path)])

    return value * partial_size / full_size


def groupfy(tree, sizes, node=None, path=None):
    """Group the nodes of the tree using an index as a metric.

    Slow recursive algorithm O(n^l) where n is the number of leaf
    nodes (lines in the KP solution) and l is the depth of the tree.

    """
    node = node if node != None else tree
    path = path or []

    name = node.attr['name']
    path = path + [name]

    # The recursive version have a gotcha. We need to groupfy all the
    # childrens before that we can test if this node can be grouped.
    for child in node.values():
        groupfy(tree, sizes, node=child, path=path)

    if node.is_preleaf():
        # Save the index value for later
        value = index(tree, sizes, path)
        if value > THRESHOLD:
            print >> sys.stderr, 'GROUPING', path, value
            node.attr['value'] = value
            node.attr['collapse'] = True
            for key in node.keys():
                del node[key]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Group files in directories. If kp is provided, the file kp is grouped. If not, the file price is grouped. You need to provide at least the price in order to compute the index.')
    parser.add_argument('--price', help='Price sorted file')
    parser.add_argument('--size', help='Size sorted file')
    parser.add_argument('--kp', help='Knapsack solution file')

    args = parser.parse_args()

    if not (args.price or args.kp) or not args.size:
        parser.print_help()
        exit(0)

    print >> sys.stderr, 'Reading size list and converting size into MB...'
    sizes = dict((s[1], s[0]) for s in read_file(args.size, ratio=B_M) if s[0] >= SIZE_CUTOFF)
    sizes_set = set(sizes.iterkeys())
    print >> sys.stderr, 'Reading price list...'
    prices = dict((p[1], p[0]) for p in read_file(args.price)
                  if p[0] >= PRICE_CUTOFF and p[1] in sizes_set)

    if args.kp:
        print >> sys.stderr, 'Reading kp file...'
        togroup = [(prices[i.strip()], i.strip()) for i in open(args.kp)]
    else:
        togroup = [(p[1], p[0]) for p in prices.iteritems()]

    print >> sys.stderr, 'Generating price tree...'
    price_tree = treefy(togroup)

    print >> sys.stderr, 'Making groups...'
    groupfy(price_tree, sizes)

    # price_tree.print_tree(rsync=True)
    price_tree.print_leaf()
