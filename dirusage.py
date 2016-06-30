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
from os.path import abspath, isdir
import argparse
from datetime import datetime as dt
import re
from termcolor import colored

__prog__    = "dirusage"
__desc__    = "Show disk usage for sub-dirs of a folder"
__version__ = "1.1"


def tree(dir,
         max_depth=1,
         min_size=0,
         padding='',
         isLast=False,
         isFirst=True,
         start_depth=None):
    depth = dir.count(os.sep)
    if start_depth is None:
        start_depth = depth
    if isFirst:
        max_depth = depth + max_depth
    if (max_depth is not None and depth >= max_depth):
        return

    pre_padding = '           '
    if depth > (start_depth + 1):
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
            print(' ' + human(dir_size(f.path)) + '  ' + prettify(f.name, "white", attrs=['bold']))
        else:
            if isLast:
                print(pre_padding + padding[:-1] + '└── ' + '[ ' + human(dir_size(f.path)) + ' ]  ' + f.name)
            else:
                print(pre_padding + padding[:-1] + '├── ' + '[ ' + human(dir_size(f.path)) + ' ]  ' + f.name)
        if isdir(path):
            if count == len(dirs):
                tree(path, max_depth, min_size, padding[:-1] + ' ', isLast, False, start_depth)
            else:
                if isFirst:
                    tree(path, max_depth, min_size, padding, isLast, False, start_depth)
                else:
                    tree(path, max_depth, min_size, padding[:-1] + '│', isLast, False, start_depth)
    return 0


def dir_size(path):
    size = 0
    for entry in scandir(path):
        if entry.is_dir(follow_symlinks=False):
            size += dir_size(entry.path)
        elif entry.is_file(follow_symlinks=False):
            size += entry.stat().st_size
    return size


def human(size, colorize=True, whole_numbers=False):
    B  = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"
    UNITS = [B, KB, MB, GB, TB]
    HUMANRADIX = 1024.

    if whole_numbers:
        format_string = '{: >3.0f} {: >2s}'
    else:
        format_string = '{: >5.1f} {: >2s}'

    if size > 500*(1024**3):
        # > 500 GB
        color = 'red'
        bg = None
    elif size > 100*(1024**3):
        # > 100 GB
        color = 'magenta'
        bg = None
    elif size > 10*(1024**3):
        # > 10 GB
        color = 'yellow'
        bg = None
    elif size > 1*(1024**3):
        # > 1 GB
        color = 'green'
        bg = None
    elif size > 100*(1024**2):
        # > 100 MB
        color = 'blue'
        bg = None
    else:
        color = None
        bg = None

    human_string = None
    for u in UNITS[:-1]:
        if size < HUMANRADIX:
            human_string = format_string.format(size, u)
            break
        size /= HUMANRADIX

    if human_string is None:
        human_string = format_string.format(size, UNITS[-1])

    if colorize:
        return prettify(human_string, color, bg)
    else:
        return human_string


def prettify(msg, color=None, bg=None, attrs=[]):
    if pretty:
        return colored(msg, color, bg, attrs)
    else:
        return msg


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
            "-c", "--colorize", action="store_true", default=False,
            help="colorize the output")
        parser.add_argument(
            "-v", "--version", action='version',
            version='%(prog)s {version}'.format(version=__version__))
        args = parser.parse_args()

        if not isdir(args.path):
            parser.error("'" + args.path + "' is not a directory")
            return 1

        global pretty
        pretty = args.colorize

        print("Current usage for " + prettify(abspath(args.path), "white", attrs=['bold']) + " at " + dt.now().strftime("%a %b %d %Y %H:%M"))
        print(prettify("(Showing folders bigger than " +
                      re.sub('^\s*([0-9.]+ [KMGT]?B)\s*$', '\g<1>', human(args.min_size * (1024**2), colorize=False, whole_numbers=True)) +
                      " up to " +
                      str(args.max_depth) +
                      (" level " if (args.max_depth == 1) else " levels ") +
                      "deep)",
                      'cyan'
             )
        )
        print()
        tree(dir=args.path, max_depth=args.max_depth, min_size=args.min_size)

        s = os.statvfs(args.path)
        print()
        print(' --------  ----------------')
        print(' ' + human(dir_size(args.path), False) + '  ' + 'total usage')
        print(' ' + human(s.f_bavail * s.f_frsize, False) + '  ' + 'free space remaining')

        return 0

    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    exit(main())
