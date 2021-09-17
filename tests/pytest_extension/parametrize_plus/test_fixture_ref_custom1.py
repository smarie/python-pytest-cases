# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_harvest import saved_fixture, get_session_synthesis_dct
from pytest_cases import parametrize, fixture_ref, fixture


has_pytest_param = hasattr(pytest, 'param')


# pytest.param is not available in all versions
if has_pytest_param:

    @pytest.fixture
    @saved_fixture
    def a():
        return 'a'


    @fixture
    @saved_fixture
    @pytest.mark.parametrize('i', [5, 6])
    def b(i):
        return 'b%s' % i


    @parametrize('arg', [pytest.param('c'),
                         pytest.param(fixture_ref(a)),
                         fixture_ref(b)],
                 hook=saved_fixture)
    def test_fixture_ref1(arg):
        assert arg in ['a', 'b5', 'b6', 'c']


    def test_synthesis1(request, fixture_store):
        results_dct1 = get_session_synthesis_dct(request, filter=test_fixture_ref1, test_id_format='function',
                                                 fixture_store=fixture_store, flatten=True)
        assert [(k, v['test_fixture_ref1_arg']) for k, v in results_dct1.items()] == [
            ('test_fixture_ref1[c]', 'c'),
            ('test_fixture_ref1[a]', 'a'),
            ('test_fixture_ref1[b-5]', 'b5'),
            ('test_fixture_ref1[b-6]', 'b6'),
        ]


    # -------------


    @pytest.fixture
    @saved_fixture
    def c():
        return 'c', 'd'


    @parametrize('foo,bar', [pytest.param(fixture_ref(a), 1),
                             (2, fixture_ref(b)),
                             pytest.param(fixture_ref(c)),
                             fixture_ref(c)
                             ])
    def test_fixture_ref2(foo, bar):
        assert foo in ['a', 2, 'c']
        assert bar in {'a': (1, ), 2: ('b5', 'b6'), 'c': ('d',)}[foo]


    def test_synthesis2(request, fixture_store):
        results_dct2 = get_session_synthesis_dct(request, filter=test_fixture_ref2, test_id_format='function',
                                                 fixture_store=fixture_store, flatten=True)
        assert list(results_dct2) == [
            'test_fixture_ref2[a-1]',
            'test_fixture_ref2[2-b-5]',
            'test_fixture_ref2[2-b-6]',
            'test_fixture_ref2[c0]',
            'test_fixture_ref2[c1]'
        ]
