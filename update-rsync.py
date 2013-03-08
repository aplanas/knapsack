#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import glob
import os
import sys

from get_path import PACKAGE


def join(path, filename):
    return os.path.join(path, filename if filename[0] != '/' else filename[1:])


def get_files(path):
    """Return the files and directories form a path."""
    files, dirs = set(), set(('/'))
    for (dirpath, dirname, filenames) in os.walk(path):
        dirpath = dirpath[len(path):]
        if dirpath:
            dirs.add(dirpath)
        files.update(os.path.join(dirpath, f) for f in filenames)
    return files, dirs


def find_packages(path, filename_prefix):
    """Use the filename_prefix to find real packages."""
    for filename in glob.glob(join(path, filename_prefix) + '*'):
        _dirname, _basename = os.path.dirname(filename), os.path.basename(filename)
        m = PACKAGE.match(_basename)
        _path = os.path.join(_dirname, m.groups()[0]) if m else filename
        if _path.endswith(filename_prefix):
            yield filename[len(path):]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Synchronize a rsync directory using hard links and an external file.')
    parser.add_argument('--src', help='Src directory')
    parser.add_argument('--dst', help='Dst directory')
    parser.add_argument('kpsol', help='Knapsack solution file')

    args = parser.parse_args()

    if not all((args.src, args.dst, args.kpsol)):
        parser.print_help()
        exit(0)

    args.src = os.path.abspath(args.src)
    src_files_to_expand = [f.strip() for f in open(args.kpsol) if f.strip()]
    src_files = set()
    for src_file in src_files_to_expand:
        src_files.update((f for f in find_packages(args.src, src_file)))
    src_dir = set(('/'))
    for src_file in src_files:
        d = os.path.dirname(src_file)
        while d != '/':
            src_dir.add(d)
            d = os.path.dirname(d)

    args.dst = os.path.abspath(args.dst)
    dst_files, dst_dir = get_files(args.dst)

    # print '** SRC DIR'
    # for i in src_dir:
    #     print i
    # print '** SRC FILES'
    # for i in src_files:
    #     print i

    new_files = src_files - dst_files
    del_files = dst_files - src_files

    new_dir = src_dir - dst_dir
    del_dir = dst_dir - src_dir

    # print '** New dirs'
    # for i in new_dir:
    #     print i
    if new_dir:
        print >> sys.stderr, 'Creating new directories ({0})...'.format(len(new_dir))
    for d in sorted(new_dir):
        d = join(args.dst, d)
        os.mkdir(d)

    # print '** New files'
    # for i in new_files:
    #     print i
    if new_files:
        print >> sys.stderr, 'Linking new files ({0})...'.format(len(new_files))
    for f in new_files:
        src, dst = join(args.src, f), join(args.dst, f)
        # print 'SRC', src
        # print 'DST', dst
        os.link(src, dst)

    # print '** Del files'
    # for i in del_files:
    #     print i
    if del_files:
        print >> sys.stderr, 'Unlinking deleted files ({0})...'.format(len(del_files))
    for f in del_files:
        f = join(args.dst, f)
        os.unlink(f)

    # print '** Del dirs'
    # for i in del_dir:
    #     print i
    if del_dir:
        print >> sys.stderr, 'Unlinking deleted directories ({0})...'.format(len(del_dir))
    for d in sorted(del_dir, reverse=True):
        d = join(args.dst, d)
        os.rmdir(d)
