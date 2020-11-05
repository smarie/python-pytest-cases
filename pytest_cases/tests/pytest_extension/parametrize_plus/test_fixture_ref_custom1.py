# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_harvest import saved_fixture, get_session_synthesis_dct
from pytest_cases import parametrize_plus, fixture_ref, pytest_fixture_plus


has_pytest_param = hasattr(pytest, 'param')


# pytest.param is not available in all versions
if has_pytest_param:

    @pytest.fixture
    @saved_fixture
    def a():
        """
        Æł¥åıĸè½¬¦ä¸ĭ¶æģģ

        Args:
        """
        return 'a'


    @pytest_fixture_plus
    @saved_fixture
    @pytest.mark.parametrize('i', [5, 6])
    def b(i):
        """
        Returns a string representation of a string

        Args:
            i: (int): write your description
        """
        return 'b%s' % i


    @parametrize_plus('arg', [pytest.param('c'),
                              pytest.param(fixture_ref(a)),
                              fixture_ref(b)],
                      hook=saved_fixture)
    def test_fixture_ref1(arg):
        """
        R test ref1 ref1.

        Args:
            arg: (todo): write your description
        """
        assert arg in ['a', 'b5', 'b6', 'c']


    def test_synthesis1(request, fixture_store):
        """
        Perform a test.

        Args:
            request: (todo): write your description
            fixture_store: (str): write your description
        """
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
        """
        Return a string with the c - c.

        Args:
        """
        return 'c', 'd'


    @parametrize_plus('foo,bar', [pytest.param(fixture_ref(a), 1),
                                  (2, fixture_ref(b)),
                                  pytest.param(fixture_ref(c)),
                                  fixture_ref(c)
                                  ])
    def test_fixture_ref2(foo, bar):
        """
        Test ref2. ref2.

        Args:
            foo: (todo): write your description
            bar: (todo): write your description
        """
        assert foo in ['a', 2, 'c']
        assert bar in {'a': (1, ), 2: ('b5', 'b6'), 'c': ('d',)}[foo]


    def test_synthesis2(request, fixture_store):
        """
        Test for flnthesis.

        Args:
            request: (todo): write your description
            fixture_store: (todo): write your description
        """
        results_dct2 = get_session_synthesis_dct(request, filter=test_fixture_ref2, test_id_format='function',
                                                 fixture_store=fixture_store, flatten=True)
        assert list(results_dct2) == [
            'test_fixture_ref2[foo_bar_is_P0]',
            'test_fixture_ref2[foo_bar_is_P1-5]',
            'test_fixture_ref2[foo_bar_is_P1-6]',
            'test_fixture_ref2[foo_bar_is_c0]',
            'test_fixture_ref2[foo_bar_is_c1]'
        ]
