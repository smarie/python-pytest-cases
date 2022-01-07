#  Authors: Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-pyfields>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-pyfields/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases
from multiprocessing import Pool, Process

from functools import partial


class TestCases:
    def case_A(self):
        return 2, 4

    def case_B(self):
        return 3, 9


def f(a, b, t):
    if t:
        assert a ** 2 == b
    else:
        # do the same..
        assert a ** 2 == b


@parametrize_with_cases("x,y", cases=TestCases)
def test_f_xy(x, y):
    # in a single process
    p = Process(target=partial(f), args=(x, y, True))
    p.start()
    p.join()

    # in a pool
    pool = Pool(processes=2)
    pool.starmap(partial(f), [(x, y, False), (x, y, True)])


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == ["test_f_xy[A]", "test_f_xy[B]"]
