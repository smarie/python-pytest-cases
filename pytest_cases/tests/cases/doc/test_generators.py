# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import sys

from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, parametrize
from pytest_cases.common_pytest_marks import has_pytest_param

from ...utils import skip


class CasesFoo:
    def case_hello(self):
        return "hello world"

    @parametrize(who=('you', skip('there')))
    def case_simple_generator(self, who):
        return "hello %s" % who


@parametrize_with_cases("msg", cases=CasesFoo)
def test_foo(msg):
    assert isinstance(msg, str) and msg.startswith("hello")


def test_foo_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo, test_id_format='function')
    assert list(results_dct) == [
        'test_foo[hello]',
        'test_foo[simple_generator-who=you]',
        # 'test_foo[simple_generator-who=there]'  skipped
    ]


class CasesFooMulti:
    def case_hello(self):
        return "hello world", len("hello world")

    @parametrize(who=(skip('you'), 'there'), **{'a,b': [(5, 5), (10, 10)]})
    def case_simple_generator(self, who, a, b):
        assert a == b
        return "hello %s" % who, len("hello %s" % who)


@parametrize_with_cases("msg,score", cases=CasesFooMulti)
def test_foo_multi(msg, score):
    assert isinstance(msg, str) and msg.startswith("hello")
    assert score == len(msg)


def test_foo_multi_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_multi, test_id_format='function')
    if sys.version_info >= (3, 6):
        # if has_pytest_param:
        assert list(results_dct) == [
            'test_foo_multi[hello]',
            # 'test_foo_multi[simple_generator-who=you]',  skipped
            # 'test_foo_multi[simple_generator-who=you]',  skipped
            'test_foo_multi[simple_generator-who=there-a=5-b=5]',
            'test_foo_multi[simple_generator-who=there-a=10-b=10]'
        ]
        # else:
        #     assert list(results_dct) == [
        #         'test_foo_multi[hello[0]-hello[1]]',
        #         # 'test_foo_multi[simple_generator-who=you]',  skipped
        #         # 'test_foo_multi[simple_generator-who=you]',  skipped
        #         'test_foo_multi[simple_generator-who=there-a=5-b=5[0]-simple_generator-who=there-a=5-b=5[1]]',
        #         'test_foo_multi[simple_generator-who=there-a=10-b=10[0]-simple_generator-who=there-a=10-b=10[1]]'
        #     ]
    else:
        assert len(results_dct) == 3
