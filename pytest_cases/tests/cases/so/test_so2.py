# from https://stackoverflow.com/a/51199035/7262247
from pytest_cases import parametrize_with_cases

try:  # python 3.2+
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


read_files = set()


@lru_cache(maxsize=3)
def load_file(file_name):
    """ This function loads the file and returns contents"""
    print("loading file " + file_name)
    global read_files
    assert file_name not in read_files
    read_files.add(file_name)
    return "<dummy content for " + file_name + ">"


def case_1():
    return load_file('file1')


def case_2():
    return load_file('file2')


def case_3():
    return load_file('file3')


@parametrize_with_cases("pars", cases=[case_1, case_2])
def test_a(pars):
    print('test_a', pars)


@parametrize_with_cases("pars", cases=[case_2, case_3])
def test_b(pars):
    print('test_b', pars)


@parametrize_with_cases("pars", cases=[case_1, case_2, case_3])
def test_c(pars):
    print('test_c', pars)
