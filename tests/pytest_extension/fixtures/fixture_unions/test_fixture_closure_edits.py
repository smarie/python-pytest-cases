# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import warnings
from copy import copy
from packaging.version import Version

import pytest

from pytest_cases.plugin import SuperClosure
from pytest_cases import fixture, fixture_union


try:
    import pytest_asyncio
except ImportError:
    PYTEST_ASYNCIO_FIXTURE = False
else:
    PYTEST_ASYNCIO_FIXTURE = Version(pytest_asyncio.__version__) >= Version('0.23.0')


@fixture(autouse=True)
def a():
    return


def test_issue116(request):
    normal_closure = request._pyfuncitem._fixtureinfo.names_closure
    assert isinstance(normal_closure, list)
    normal_closure.remove('a')


with warnings.catch_warnings():
    # ignore the warning about the two values being the same fixture.
    warnings.simplefilter("ignore")
    b = fixture_union('b', [a, a])


super_closure = None


def test_super_closure_edits(request, b):
    # save for later
    global super_closure
    super_closure = request._pyfuncitem._fixtureinfo.names_closure


def test_super_closure_edits2():
    global super_closure
    assert isinstance(super_closure, SuperClosure)
    super_closure = copy(super_closure)
    reflist = ['environment', 'a', 'request', 'b']
    if PYTEST_ASYNCIO_FIXTURE:
        reflist = ['event_loop_policy'] + reflist
    assert len(super_closure) == len(reflist)
    assert list(super_closure) == reflist
    assert super_closure[:] == reflist[:]
    assert super_closure[1] == reflist[1]
    assert super_closure[-1] == reflist[-1]
    assert super_closure[::-2] == reflist[::-2]

    # edit without modifications are allowed
    super_closure[1] = reflist[1]
    super_closure[::2] = reflist[::2]
    with pytest.warns(UserWarning):
        super_closure[2+PYTEST_ASYNCIO_FIXTURE:] = ['b', 'request']
        # the above operation is allowed but does nothing and a warning is issued.
        assert super_closure[2+PYTEST_ASYNCIO_FIXTURE:] == ['request', 'b']

    # removing now works
    super_closure.remove('request')
    reflist.remove('request')
    assert list(super_closure) == reflist

    with pytest.raises(NotImplementedError):
        # 'b' is a split fixture so we cannot remove it
        del super_closure[-1]
    # we can remove the 'environment' one
    del super_closure[0]
    del reflist[0]
    if PYTEST_ASYNCIO_FIXTURE:
        # remove event_loop_policy and environment
        del super_closure[0]
        del reflist[0]
    assert list(super_closure) == reflist

    # now supported
    super_closure.append('toto')
    reflist.append('toto')
    assert list(super_closure) == reflist

    # inserting at a random position does not work
    with pytest.raises(NotImplementedError):
        super_closure.insert(1, 'titi')

    # but inserting at the beginning works
    super_closure.insert(0, 'titi')
    reflist.insert(0, 'titi')
    assert list(super_closure) == reflist
