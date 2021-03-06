import errno
import os
import sys

import numpy as np


def make_dir_check_writable(path: str):
    """
    Create `path`, if needed, and check that leaf directory is writable.
    Does *not* remove nor change permissions on existing files and directories.
    Raises error if task can't be accomplished.

    Parameters:
        * path (str): directory to create

    Returns:
        * str: absolute path of directory

    Raises:
        * NotADirectoryError: if path or any anchestor exists and is not a
            directory
        * PermissionError: if path or any anchestor can't be created because
        of missing permission, or path is not writable

    Error codes from: https://docs.python.org/3/library/errno.html
    """
    path = os.path.realpath(path)

    # make sure path exists
    acc = path[0]
    for d in path.split(os.sep):
        acc = os.path.join(acc, d)
        try:
            os.mkdir(acc)
        except FileExistsError:
            if not os.path.isdir(acc):
                raise NotADirectoryError(
                        errno.ENOTDIR, "Not a directory: '%s'" % acc)
            # dir exists

    # check leaf is writable
    if not os.access(path, os.W_OK | os.X_OK):
        raise PermissionError(
                errno.EACCES, "Permission denied: '%s'" % path)

    return path


def map_to_int(input_list: list, forced: bool = False):
    """
    Return map of integer values for items in input_list.

    If forced is False (default), returned map is empty if any item from
    input_list can't be converted to integer.
    If forced is True, returned map contains items from input_list that
    can be converted only.

    Parameters:
        * input_list (list): iterable of items to convert
        * forced (bool): force conversion whether possible

    Returns:
        * dict: keys is subset of input_list, values are corresponding integer
        values; it will be empty if any of the following events occurs:
            - input_list is empty
            - forced is False and one or more items can't be converted
            - forced is True and no item can be converted
    """
    map = {}
    for s in input_list:
        try:
            map[s] = int(s)
        except (TypeError, ValueError):
            if not forced:
                return {}
    return map


def string_to_linspace(string: str):
    """
    Parse string to generate an evenly spaced list of numbers.
    The string format is: [START[,STOP[,NUM]]

    Parameters:
        * string (str): comma-separated representation of:
            - start (float): first sample
            - stop (float, optional): last sample; default is `start`
            - num (int, optional): number of samples; default is 11

    Returns:
        * Iterable: linear space generated from the parsed string

    Raises:
        * TypeError: if string cannot be split into 1, 2 or 3 parts
        * ValueError: if any part of the string cannot be converted to its
        target type
    """
    # split string
    params = string.split(',')
    if len(params) == 1:
        return [float(string)]
    if not len(params) in (2, 3):
        msg = 'expected 2 or 3 comma-separated values, got %s' % len(params)
        raise TypeError(msg)
    # parse np.linspace params
    start, stop = [float(s) for s in params[:2]]
    num = int(params[2]) if len(params) == 3 else 11
    # round up to 8 decimal digits
    return np.round(np.linspace(start, stop, num), 8)


def die(package: str, exception: Exception):
    """
    Gracefully print exception error and die.

    Parameters:
        * package (str): package invoking this function
        * exception (Exception): unhandled exception to print
    """
    msg = "%s: error: %s" % (package, exception)
    print(msg, file=sys.stderr)
    sys.exit(1)


def uid_to_path(directory: str, prefix: str) -> str:
    """
    Return path of file in directory whose name starts with prefix.
    Raises error if zero or more than one file is found.

    Parameters:
        * directory (str): directory to search a matching file in
        * prefix (str): UID prefix to search for a matching file

    Returns:
        * str: matching file path

    Raises:
        * NotADirectoryError: if directory is not a directory
        * FileNotFoundError: if no file or too many files in directory are
        matching prefix
    """
    candidates = [f for f in os.listdir(directory) if f.startswith(prefix)
                  and os.path.isfile(os.path.join(directory, f))]
    if not candidates:
        raise FileNotFoundError(
                errno.ENOENT, "No matching file in '%s' for UID '%s'." %
                (directory, prefix))
    if len(candidates) > 1:
        raise FileNotFoundError(
                errno.ENOKEY, "Too many matching files in '%s' for UID '%s'." %
                (directory, prefix))
    return os.path.join(directory, candidates[0])
