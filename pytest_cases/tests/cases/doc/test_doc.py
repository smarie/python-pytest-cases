import pytest

from pytest_harvest import get_session_synthesis_dct
from pytest_cases import parametrize_with_cases, AUTO2, fixture_plus

from . import cases_doc
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
    assert list(results_dct) == ['test_foo_default_cases_file[two_positive_ints]',
                                 'test_foo_default_cases_file[two_negative_ints]']


@parametrize_with_cases("a,b", cases=AUTO2)
def test_foo_alternate_cases_file_and_one_marked_skip(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_alternate_cases_file_and_one_marked_skip_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_alternate_cases_file_and_one_marked_skip,
                                            test_id_format='function')
    assert list(results_dct) == [# 'test_foo_default_cases_file[two_positive_ints]', skipped
                                 'test_foo_alternate_cases_file_and_one_marked_skip[two_negative_ints]']


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
    assert list(results_dct) == ['test_foo_fun_list[strange_ints0]',
                                 'test_foo_fun_list[strange_ints1]']


class CasesFoo:
    @classmethod
    def case_toto(cls):
        return

    @staticmethod
    def case_foo():
        return

    def case_two_negative_ints(self):
        """ Inputs are two negative integers """
        return -1, -2


@parametrize_with_cases("a,b", cases=CasesFoo)
def test_foo_cls(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_cls_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_cls, test_id_format='function')
    assert list(results_dct) == ['test_foo_cls[two_negative_ints]']


@parametrize_with_cases("a,b", cases=(CasesFoo, strange_ints, cases_doc, CasesFoo, '.test_doc_cases'))
def test_foo_cls_list(a, b):
    assert isinstance(foo(a, b), tuple)


def test_foo_cls_list_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_cls_list, test_id_format='function')
    assert list(results_dct) == [
        # CasesFoo
        'test_foo_cls_list[two_negative_ints0]',
        # strange_ints
        'test_foo_cls_list[strange_ints]',
        # cases_doc.py
        'test_foo_cls_list[two_negative_ints1]',
        # CasesFoo
        'test_foo_cls_list[two_negative_ints2]',
        # test_doc_cases.py
        'test_foo_cls_list[two_positive_ints1]',
        'test_foo_cls_list[two_negative_ints3]'
    ]


@fixture_plus
@parametrize_with_cases("a,b")
def c(a, b):
    return a + b


def test_foo_parametrize_fixture(c):
    assert isinstance(c, int)


def test_foo_parametrize_fixture_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo_parametrize_fixture, test_id_format='function')
    assert list(results_dct) == ['test_foo_parametrize_fixture[two_positive_ints]',
                                 'test_foo_parametrize_fixture[two_negative_ints]']
