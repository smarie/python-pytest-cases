# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
#
# This is a more complex version of test_fixture_union_setup_teardown3.py
# but the idea is the same: find a configuration in which the "smart reordering" of pytest
# can not group test nodes together, so that we have session- and module-scoped fixtures
# used and not used, alternatively. The objective is to check that they are not called several times
# in spite of them being used/not used alternatively in test nodes.
#
from collections import defaultdict

from pytest_cases import fixture, fixture_union, parametrize

used = defaultdict(lambda: False)
torn_down = defaultdict(lambda: False)


@fixture(scope='session')
def s1():
    """
    A context manager for s1 s1.

    Args:
    """
    name = 's1'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='session')
def s2():
    """
    A context manager that creates a context manager.

    Args:
    """
    name = 's2'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='session')
def s3():
    """
    A context manager to the s3.

    Args:
    """
    name = 's3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='module')
def M1s1s2(s1, s2):
    """
    Yields1s1s2s2s2s2s2s2s2s2s2s2s2s2

    Args:
        s1: (todo): write your description
        s2: (todo): write your description
    """
    name = 'M1s1s2'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='module')
def M2s1s3(s1, s3):
    """
    A context manager names1s3s3s3s3s3s3s3s3s3s3s3s3

    Args:
        s1: (int): write your description
        s3: (int): write your description
    """
    name = 'M2s1s3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
def F1M1s1s2(M1s1s2):
    """
    A context manager which returns the two sets.

    Args:
        M1s1s2: (todo): write your description
    """
    name = 'F1M1s1s2'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
@parametrize(i=[0, 1])
def F2(i):
    """
    A context manager to the current context.

    Args:
        i: (int): write your description
    """
    name = 'F2(%s)' % i
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
def F3s2s3(s2, s3):
    """
    A context manager to s3s2s2.

    Args:
        s2: (todo): write your description
        s3: (int): write your description
    """
    name = 'F3s2s3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
def F4M2s1s3(M2s1s3):
    """
    A context manager for s1s1s3s3s3s3s3s3s3s3s3s3s3

    Args:
        M2s1s3: (int): write your description
    """
    name = 'F4M2s1s3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


d = fixture_union('d', (F1M1s1s2, F2, F3s2s3, F4M2s1s3))


super_closure = None


def test_foo(d, request):
    """
    Set the test test test test test.

    Args:
        d: (todo): write your description
        request: (todo): write your description
    """
    # store closure for later analysis or test
    global super_closure
    super_closure = request._pyfuncitem._fixtureinfo.names_closure


def test_synthesis(module_results_dct):
    """
    Synthesis of all modules.

    Args:
        module_results_dct: (todo): write your description
    """
    assert all(torn_down.values())
    assert list(module_results_dct) == [
        'test_foo[d_is_F1M1s1s2]',
        'test_foo[d_is_F2-i=0]',
        'test_foo[d_is_F2-i=1]',
        'test_foo[d_is_F3s2s3]',
        'test_foo[d_is_F4M2s1s3]'
    ]

    function_scoped = ('F1M1s1s2', 'F2(0)', 'F2(1)', 'F3s2s3', 'F4M2s1s3')
    module_scoped = ('M1s1s2', 'M2s1s3')
    session_scoped = ('s1', 's2', 's3')

    for item in function_scoped + module_scoped + session_scoped:
        assert used[item] == 1, "item %s was not used once" % item

        if item in function_scoped:
            assert torn_down[item] == 1, "item %s was not torn down once" % item
        # else we know that the last module/session fixture alive is not properly torn down, this is a pytest issue


# def test_super_closure():
#     global super_closure
#     print(super_closure)
