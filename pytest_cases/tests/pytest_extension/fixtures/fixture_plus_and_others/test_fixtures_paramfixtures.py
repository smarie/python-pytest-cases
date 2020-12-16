# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import param_fixture, param_fixtures, fixture


# pytest.param - not available in all versions
has_pytest_param = hasattr(pytest, 'param')
if has_pytest_param:
    pytest_param = pytest.param
else:
    def pytest_param(*args, **kwargs):
        return args


# ---------- (1)
# create a single parameter fixture with and without explicit symbol creation
param_fixture("my_parameter", [1, 2])
my_parameter2 = param_fixture("my_parameter2", [3, 4])  # Returning value


@pytest.fixture
def fixture_uses_param(my_parameter, my_parameter2):
    return my_parameter, my_parameter2


def test_uses_param(my_parameter, my_parameter2, fixture_uses_param):
    # check that the parameter injected in both is the same
    assert my_parameter, my_parameter2 == fixture_uses_param


# ---------- (2)
# create a 2-tuple parameter fixture without symbol creation
param_fixtures("arg1, arg2", [(1, 2), (3, 4)])

# Testing param_fixtures with single arg
arg3 = param_fixture("arg3", [5, 6])


@pytest.fixture
def fixture_uses_param2(arg2):
    return arg2


def test_uses_param2(arg1, arg2, arg3, fixture_uses_param2):
    # check that the parameter injected in both is the same
    assert arg2 == fixture_uses_param2
    assert arg1, arg2 in [(1, 2), (3, 4)]
    assert arg3 in [5, 6]


# ---------- (3)
param_fixtures("parg1, parg2", [("a", "b"), ("c", "d")])
"""Two parameter fixtures"""


@fixture
@pytest.mark.parametrize("arg1, arg2", [
    pytest_param(1, 2, id="f_a"),
    pytest_param(3, 4, id="f_b")
])
def myfix(arg1, arg2, parg1):
    """One parameterized fixture relying on above param fixture"""
    return arg1, arg2, parg1


@pytest.mark.parametrize("arg3, arg4", [
    pytest_param(10, 20, id="t_a"),
    pytest_param(30, 40, id="t_b")
])
def test_custom_parameters(myfix, arg3, arg4, parg1, parg2, request):
    """"""
    assert myfix[2] == parg1
    paramvalues = request.node.nodeid.split('[')[1][:-1]
    if has_pytest_param:
        arg1arg2id = "f_a" if myfix[:-1] == (1, 2) else "f_b"
        arg3arg4id = "t_a" if (arg3, arg4) == (10, 20) else "t_b"
    else:
        arg1arg2id = "-".join(["%s" % v for v in myfix[:-1]])
        arg3arg4id = "-".join(["%s" % v for v in (arg3, arg4)])

    assert paramvalues == "{}-{}-{}-{}".format(arg1arg2id, parg1, parg2, arg3arg4id)
    # print("parg1={} parg2={} myfix={} arg3={} arg4={}".format(parg1, parg2, myfix, arg3, arg4))


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """

    end_list = ['test_custom_parameters[f_a-a-b-t_a]',
                'test_custom_parameters[f_a-a-b-t_b]',
                'test_custom_parameters[f_a-c-d-t_a]',
                'test_custom_parameters[f_a-c-d-t_b]',
                'test_custom_parameters[f_b-a-b-t_a]',
                'test_custom_parameters[f_b-a-b-t_b]',
                'test_custom_parameters[f_b-c-d-t_a]',
                'test_custom_parameters[f_b-c-d-t_b]']

    if not has_pytest_param:
        end_list = [s.replace('t_a', '10-20')
                        .replace('t_b', '30-40')
                        .replace('f_a', '1-2')
                        .replace('f_b', '3-4') for s in end_list]

    assert list(module_results_dct) == ['test_uses_param[1-3]',
                                        'test_uses_param[1-4]',
                                        'test_uses_param[2-3]',
                                        'test_uses_param[2-4]',
                                        # see https://github.com/pytest-dev/pytest/issues/5054
                                        # -> fixed by latest pytest-cases
                                        'test_uses_param2[1-2-5]',
                                        'test_uses_param2[1-2-6]',
                                        'test_uses_param2[3-4-5]',
                                        'test_uses_param2[3-4-6]',
                                        # 'test_uses_param2[5-1-2]',
                                        # 'test_uses_param2[5-3-4]',
                                        # 'test_uses_param2[6-1-2]',
                                        # 'test_uses_param2[6-3-4]',
                                        ] + end_list
