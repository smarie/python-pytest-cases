from distutils.version import LooseVersion

import pytest

from pytest_harvest import saved_fixture, get_session_synthesis_dct
from pytest_cases import parametrize_plus, fixture_ref, pytest_fixture_plus


# pytest.param is not available in all versions
if LooseVersion(pytest.__version__) >= LooseVersion('3.0.0'):

    @pytest.fixture
    @saved_fixture
    def a():
        return 'a'


    @pytest_fixture_plus
    @saved_fixture
    @pytest.mark.parametrize('i', [5, 6])
    def b(i):
        return 'b%s' % i


    @parametrize_plus('arg', [pytest.param('c'),
                              pytest.param(fixture_ref(a)),
                              fixture_ref(b)],
                      hook=saved_fixture)
    def test_fixture_ref1(arg):
        assert arg in ['a', 'b5', 'b6', 'c']


    def test_synthesis1(request, fixture_store):
        results_dct1 = get_session_synthesis_dct(request, filter=test_fixture_ref1, test_id_format='function',
                                                 fixture_store=fixture_store, flatten=True)
        assert [(k, v['test_fixture_ref1_arg']) for k, v in results_dct1.items()] == [
            ('test_fixture_ref1[arg_is_c]', 'c'),
            ('test_fixture_ref1[arg_is_a]', 'a'),
            ('test_fixture_ref1[arg_is_b-5]', 'b5'),
            ('test_fixture_ref1[arg_is_b-6]', 'b6'),
        ]


    # -------------


    @pytest.fixture
    @saved_fixture
    def c():
        return 'c', 'd'


    @parametrize_plus('foo,bar', [pytest.param(fixture_ref(a), 1),
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
            'test_fixture_ref2[foo_bar_is_P0]',
            'test_fixture_ref2[foo_bar_is_P1-5]',
            'test_fixture_ref2[foo_bar_is_P1-6]',
            'test_fixture_ref2[foo_bar_is_c0]',
            'test_fixture_ref2[foo_bar_is_c1]'
        ]
