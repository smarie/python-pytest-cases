# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_harvest import get_session_synthesis_dct
from pytest_cases import parametrize_with_cases, fixture, case, AUTO

from . import cases_doc_alternate
from .example import foo


@pytest.mark.parametrize("a,b", [(1, 2), (-1, -2)])
def test_foo1(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo1_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo1, test_id_format='function')
    assert list(results_dct) == ['test_foo1[1-2]', 'test_foo1[-1--2]']


@parametrize_with_cases("a,b")
def test_foo_default_cases_file(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_default_cases_file_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_default_cases_file, test_id_format='function')
    assert list(results_dct) == [
        'test_foo_default_cases_file[two_positive_ints]',
        'test_foo_default_cases_file[two_negative_ints]'
    ]


def strange_ints():
    """ Inputs are two negative integers """
    return -1, -2


@parametrize_with_cases("a,b", cases=strange_ints)
def test_foo_fun(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_fun_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_fun, test_id_format='function')
    assert list(results_dct) == ['test_foo_fun[strange_ints]']


@parametrize_with_cases("a,b", cases=(strange_ints, strange_ints))
def test_foo_fun_list(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_fun_list_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_fun_list, test_id_format='function')
    assert list(results_dct) == [
        'test_foo_fun_list[strange_ints0]',
        'test_foo_fun_list[strange_ints1]'
    ]


class CasesFoo:
    @classmethod
    def case_toto(cls):
        return 0, 0

    @staticmethod
    def case_foo():
        return 0, 0

    @pytest.mark.skipif(False, reason="no")
    @case(id="hello world")
    def case_blah(self):
        """a blah"""
        return 0, 0

    @pytest.mark.skip
    def case_skipped(self):
        """skipped case"""
        return 0

    def case_two_negative_ints(self):
        """ Inputs are two negative integers """
        return -1, -2


@parametrize_with_cases("a,b", cases=CasesFoo)
def test_foo_cls(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_cls_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_cls, test_id_format='function')
    assert list(results_dct) == [
        'test_foo_cls[toto]',
        'test_foo_cls[foo]',
        'test_foo_cls[hello world]',
        'test_foo_cls[two_negative_ints]'
    ]


@parametrize_with_cases("a,b", cases=(CasesFoo, strange_ints, cases_doc_alternate, CasesFoo, '.test_doc_cases'))
def test_foo_cls_list(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_cls_list_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_cls_list, test_id_format='function')
    ref_list = [
        # CasesFoo
        'test_foo_cls_list[toto0]',
        'test_foo_cls_list[foo0]',
        'test_foo_cls_list[hello world0]',
        'test_foo_cls_list[two_negative_ints0]',
        # strange_ints
        'test_foo_cls_list[strange_ints]',
        # cases_doc_alternate.py
        'test_foo_cls_list[toto1]',
        'test_foo_cls_list[foo1]',
        'test_foo_cls_list[hello]',
        'test_foo_cls_list[two_negative_ints1]',
        'test_foo_cls_list[two_negative_ints2]',
        # CasesFoo
        'test_foo_cls_list[toto2]',
        'test_foo_cls_list[foo2]',
        'test_foo_cls_list[hello world1]',
        'test_foo_cls_list[two_negative_ints3]',
        # test_doc_cases.py
        'test_foo_cls_list[two_positive_ints]',
        'test_foo_cls_list[two_negative_ints4]'
    ]
    assert list(results_dct) == ref_list


@fixture
@parametrize_with_cases("a,b", cases=AUTO)  # just checking that explicit AUTO is same as implicit
def c(a, b):
    return a + b


def test_foo_parametrize_fixture(c):
    assert isinstance(c, int)


def test_foo_parametrize_fixture_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_parametrize_fixture, test_id_format='function')
    assert list(results_dct) == ['test_foo_parametrize_fixture[two_positive_ints]',
                                 'test_foo_parametrize_fixture[two_negative_ints]']
