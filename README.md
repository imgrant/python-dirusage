# python-dirusage
Show disk usage for sub-dirs of a folder, with control over depth recursion and minimum size to display.

Adapted from Doug Dahms' tree.py

Like `du --max-depth=1`, dirusage lists the size of sub-dirs in the given directory.
Additional parameters allow the recursion to go deeper, displayed as a tree, and also to only display folders bigger than a given size.
Folders are automatically sorted by size.

## Summary
usage: dirusage [-h] [-d MAX_DEPTH] [-s MIN_SIZE] [-v] path

positional arguments:
  path                  root folder to calculate the tree for

optional arguments:
  -h, --help            show this help message and exit
  -d MAX_DEPTH, --max-depth MAX_DEPTH
                        maximum recursion depth to draw the tree to (default
                        is 1, immediate sub-dirs only)
  -s MIN_SIZE, --min-size MIN_SIZE
                        minimum folder size (MB) to draw branches for
  -v, --version         show program's version number and exit
