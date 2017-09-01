import os
import copy


def _merge(a, b):
    """ a overwrites values in b
    """

    for k in a.keys():
        if isinstance(a[k], dict) and k in b and isinstance(b[k], dict):
            b[k] = _merge(a[k], b[k])
        else:
            b[k] = a[k]
    return b


def merge(a, b):
    """ makes copies before merging
    """

    return _merge(copy.deepcopy(a), copy.deepcopy(b))


def get_directories(path):
    """ returns a list of directory names from `path`
    """

    try:
        directories = []
        for directory in os.listdir(path):
            directory_path = os.path.join(path, directory)
            if os.path.isdir(directory_path):
                directories.append(directory)

    except Exception as e:
        # TODO: handle exception
        # TODO: logging, raise FileNotFoundError, PermissionError
        raise

    return directories


def create_directory(path):
    """ creates a directory at `path`
    """

    try:
        os.makedirs(path)

    except Exception as e:
        # TODO: handle exception
        # TODO: logging, raise FileNotFoundError, PermissionError
        raise

    return True
