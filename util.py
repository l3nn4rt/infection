import os
import sys

def mkdir_p(path: str):
    """
    Emulate native `mkdir -p`.

    Parameters:
        * path (str): directory to create

    Returns:
        str: absolute path of directory
    """
    path = os.path.realpath(path)
    acc = path[0]
    for d in path.split(os.sep):
        acc = os.path.join(acc, d)
        try:
            os.mkdir(acc)
        except FileExistsError: # dir exists
            pass
    return path

def map_to_int(input_list: list, forced:bool=False) -> dict[object, int]:
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
