import os

__all__ = ['find_file', 'rel_path', 'read_file_line']


def find_file(path: str, filename: str):
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn == filename:
                return os.path.join(root, fn)
    raise FileNotFoundError(filename)


def rel_path(relative_path: str) -> str:
    from os.path import dirname, join, abspath, isabs
    if isabs(relative_path):
        return relative_path
    bdir = dirname(__file__)
    joinpath = join(bdir, relative_path)
    return abspath(joinpath)


def read_file_line(filepath: str) -> str:
    with open(filepath, "r") as fd:
        return fd.readline().rstrip("\n")

