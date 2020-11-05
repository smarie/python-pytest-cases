# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import sys

from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, parametrize
from pytest_cases.common_pytest import has_pytest_param

from ...utils import skip


class CasesFoo:
    def case_hello(self):
        """
        Returns a string representation of the case.

        Args:
            self: (todo): write your description
        """
        return "hello world"

    @parametrize(who=('you', skip('there')))
    def case_simple_generator(self, who):
        """
        : param who : class : param who : a generator

        Args:
            self: (todo): write your description
            who: (str): write your description
        """
        return "hello %s" % who


@parametrize_with_cases("msg", cases=CasesFoo)
def test_foo(msg):
    """
    Convert a test message to a test.

    Args:
        msg: (str): write your description
    """
    assert isinstance(msg, str) and msg.startswith("hello")


def test_foo_synthesis(request):
    """
    Test if the test test results.

    Args:
        request: (todo): write your description
    """
    results_dct = get_session_synthesis_dct(request, filter=test_foo, test_id_format='function')
    assert list(results_dct) == [
        'test_foo[hello]',
        'test_foo[simple_generator-who=you]',
        # 'test_foo[simple_generator-who=there]'  skipped
    ]


class CasesFooMulti:
    def case_hello(self):
        """
        Returns a string representation of - case case - case.

        Args:
            self: (todo): write your description
        """
        return "hello world", len("hello world")

    @parametrize(who=(skip('you'), 'there'), **{'a,b': [(5, 5), (10, 10)]})
    def case_simple_generator(self, who, a, b):
        """
        Generate a simple generator.

        Args:
            self: (todo): write your description
            who: (str): write your description
            a: (todo): write your description
            b: (todo): write your description
        """
        assert a == b
        return "hello %s" % who, len("hello %s" % who)


@parametrize_with_cases("msg,score", cases=CasesFooMulti)
def test_foo_multi(msg, score):
    """
    Evaluate test test.

    Args:
        msg: (str): write your description
        score: (todo): write your description
    """
    assert isinstance(msg, str) and msg.startswith("hello")
    assert score == len(msg)


def test_foo_multi_synthesis(request):
    """
    Convert a list of a list of a request.

    Args:
        request: (todo): write your description
    """
    results_dct = get_session_synthesis_dct(request, filter=test_foo_multi, test_id_format='function')
    if sys.version_info >= (3, 6):
        if has_pytest_param:
            assert list(results_dct) == [
                'test_foo_multi[hello]',
                # 'test_foo_multi[simple_generator-who=you]',  skipped
                # 'test_foo_multi[simple_generator-who=you]',  skipped
                'test_foo_multi[simple_generator-who=there-a=5-b=5]',
                'test_foo_multi[simple_generator-who=there-a=10-b=10]'
            ]
        else:
            assert list(results_dct) == [
                'test_foo_multi[hello[0]-hello[1]]',
                # 'test_foo_multi[simple_generator-who=you]',  skipped
                # 'test_foo_multi[simple_generator-who=you]',  skipped
                'test_foo_multi[simple_generator-who=there-a=5-b=5[0]-simple_generator-who=there-a=5-b=5[1]]',
                'test_foo_multi[simple_generator-who=there-a=10-b=10[0]-simple_generator-who=there-a=10-b=10[1]]'
            ]
    else:
        assert len(results_dct) == 3
