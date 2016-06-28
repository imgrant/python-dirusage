#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# dirusage.py
#
# Written by Ian Grant, adapted from Doug Dahms
#
# Like 'du --max-depth=1', dirusage lists the size
# of sub-dirs in the given directory.
# Additional parameters allow the recursion to go
# deeper, displayed as a tree, and also to only
# display folders bigger than a given size.
# Folders are automatically sorted by size.
#

from sys import exit
import os
from os import scandir
from os.path import abspath, basename, isdir
import argparse
from datetime import datetime as dt

__prog__    = "dirusage"
__desc__    = "Show disk usage for sub-dirs of a folder"
__version__ = "1.0"


def tree(dir,
         max_depth=1,
         min_size=0,
         padding='',
         isLast=False,
         isFirst=True):
    depth = dir.count(os.sep)
    if (max_depth is not None and depth >= max_depth):
        return

    pre_padding = '           '
    if depth > 1:
        padding = padding + '                  '

    dirs = [x for x in scandir(dir) if x.is_dir()]    
    dirs = sorted((d for d in dirs if dir_size(d.path) >= (min_size * 1024**2)),
                    key=lambda s: dir_size(s.path),
                    reverse=True)
    count = 0
    last = len(dirs) - 1
    for i, f in enumerate(dirs):
        count += 1
        path = dir + os.sep + f.name
        isLast = i == last
        if isFirst:
            print(' ' + human(dir_size(f.path)) + '  ' + f.name)
        else:
            if isLast:
                print(pre_padding + padding[:-1] + '└── ' + '[ ' + human(dir_size(f.path)) + ' ]  ' + f.name)
            else:
                print(pre_padding + padding[:-1] + '├── ' + '[ ' + human(dir_size(f.path)) + ' ]  ' + f.name)
        if isdir(path):
            if count == len(dirs):
                tree(path, max_depth, min_size, padding[:-1] + ' ', isLast, False)
            else:
                if isFirst:
                    tree(path, max_depth, min_size, padding, isLast, False)
                else:
                    tree(path, max_depth, min_size, padding[:-1] + '│', isLast, False)
    return 0


def dir_size(path):
    size = 0
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            size += dir_size(entry.path)
        elif entry.is_file(follow_symlinks=False):
            size += entry.stat().st_size
    return size


def human(size):
    B  = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"
    UNITS = [B, KB, MB, GB, TB]
    HUMANFMT = "%5.1f % 2s"
    HUMANRADIX = 1024.

    for u in UNITS[:-1]:
        if size < HUMANRADIX:
            return HUMANFMT % (size, u)
        size /= HUMANRADIX

    return HUMANFMT % (size, UNITS[-1])


def main():
    try:
        parser = argparse.ArgumentParser(prog=__prog__)
        parser.add_argument(
            "path", help="root folder to calculate the tree for")
        parser.add_argument(
            "-d", "--max-depth", action="store", default=1, type=int,
            help="maximum recursion depth to draw the tree to (default is 1, immediate sub-dirs only)")
        parser.add_argument(
            "-s", "--min-size", action="store", default=0, type=float,
            help="minimum folder size (MB) to draw branches for")
        parser.add_argument(
            "-v", "--version", action='version',
            version='%(prog)s {version}'.format(version=__version__))
        args = parser.parse_args()

        if not isdir(args.path):
            parser.error("'" + args.path + "' is not a directory")
            return 1

        print("Current usage for " + abspath(args.path) + " at " + dt.now().strftime("%a %b %d %Y %H:%M:"))
        tree(dir=args.path, max_depth=args.max_depth, min_size=args.min_size)

        s = os.statvfs(args.path)
        print(' --------  ----------------')
        print(' ' + human(dir_size(args.path)) + '  ' + 'total usage')
        print(' ' + human(s.f_bavail * s.f_frsize) + '  ' + 'free space remaining')

        return 0

    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    exit(main())
