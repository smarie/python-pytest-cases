# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from copy import copy

import pytest

from pytest_cases.plugin import SuperClosure
from pytest_cases import fixture, fixture_union


@fixture(autouse=True)
def a():
    return


def test_issue116(request):
    normal_closure = request._pyfuncitem._fixtureinfo.names_closure
    assert isinstance(normal_closure, list)
    normal_closure.remove('a')


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
    assert len(super_closure) == 4
    assert list(super_closure) == ['environment', 'a', 'request', 'b']
    reflist = list(super_closure)
    assert super_closure[:] == reflist[:]
    assert super_closure[1] == reflist[1]
    assert super_closure[-1] == reflist[-1]
    assert super_closure[::-2] == reflist[::-2]

    # edit without modifications are allowed
    super_closure[1] = reflist[1]
    super_closure[::2] = reflist[::2]
    with pytest.warns(UserWarning):
        super_closure[2:] = ['b', 'request']
        # the above operation is allowed but does nothing and a warning is issued.
        assert super_closure[2:] == ['request', 'b']

    with pytest.raises(NotImplementedError):
        super_closure.remove('request')

    with pytest.raises(NotImplementedError):
        del super_closure[-1]

    # now supported
    super_closure.append('toto')
    assert list(super_closure) == ['environment', 'a', 'request', 'b', 'toto']

    with pytest.raises(NotImplementedError):
        super_closure.insert(0, 'toto')
