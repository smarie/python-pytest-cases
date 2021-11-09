# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import parametrize
from pytest_cases.common_pytest import get_callspecs
from pytest_cases.common_pytest_marks import has_pytest_param


if not has_pytest_param:
    @pytest.mark.parametrize('new_style', [False, True])
    def test_getcallspecs(new_style):
        if new_style:
            parametrizer = parametrize(a=[1, pytest.mark.skipif(True)('12')], idgen="a={a}")
        else:
            parametrizer = parametrize('a', [1, pytest.mark.skipif(True)('12')], ids=['oh', 'my'])

        @parametrizer
        def test_foo(a):
            pass

        calls = get_callspecs(test_foo)

        assert len(calls) == 2
        assert calls[0].funcargs == dict(a=1)
        assert calls[0].id == 'a=1' if new_style else 'oh'
        assert calls[0].marks == []

        assert calls[1].funcargs == dict(a='12')
        ref_id = "a=12" if new_style else 'my'
        assert calls[1].id == ref_id
        assert calls[1].marks[0].name == 'skipif'

else:
    @pytest.mark.parametrize('new_style', [False, True])
    def test_getcallspecs(new_style):
        if new_style:
            parametrizer = parametrize(a=[1, pytest.param('12', marks=pytest.mark.skip)], idgen="a={a}")
        else:
            parametrizer = parametrize('a', [1, pytest.param('12', marks=pytest.mark.skip, id='hey')], ids=['oh', 'my'])

        @parametrizer
        def test_foo(a):
            pass

        calls = get_callspecs(test_foo)

        assert len(calls) == 2
        assert calls[0].funcargs == dict(a=1)
        assert calls[0].id == 'a=1' if new_style else 'oh'
        assert calls[0].marks == []

        assert calls[1].funcargs == dict(a='12')
        assert calls[1].id == 'a=12' if new_style else 'hey'
        assert calls[1].marks[0].name == 'skip'
