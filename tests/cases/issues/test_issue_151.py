import sys

import itertools

import pytest
from pytest_cases.common_pytest_marks import has_pytest_param

from pytest_cases import parametrize_with_cases, case, get_case_id


@pytest.fixture
def barToFoo():
    pass


@case(id="simple")
def case_depends_on_fixture(barToFoo):
    inputs = ["foo", "bar"]
    request_data = {"foo": "dfg", "data": "asd"}
    return inputs, request_data


@parametrize_with_cases("inputs,request_data", cases=case_depends_on_fixture, idstyle='explicit')
def test_create_fixture_idstyle_explicit(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_depends_on_fixture, ids=("custom{%i}" % i for i in itertools.count()))
def test_create_fixture_ids_generator(inputs, request_data):
    pass


def mygen(o):
    # sort alphabetically to preserve order on continuous integration builds
    return "hello_%s" % get_case_id(o) # "_".join("%s=%s" % (k, kwargs[k]) for k in sorted(kwargs.keys()))


@parametrize_with_cases("inputs,request_data", cases=case_depends_on_fixture, ids=mygen)
def test_create_fixture_ids_callable(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_depends_on_fixture, idstyle=str)
def test_create_fixture_ids_callable_str(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_depends_on_fixture, idstyle="compact")
def test_create_fixture_idstyle_compact(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_depends_on_fixture)  # , idstyle=None
def test_create_fixture_idstyle_none(inputs, request_data):
    pass


@case(id="simple")
def case_does_not_depend_on_fixture():
    inputs = ["foo", "bar"]
    request_data = {"foo": "dfg", "data": "asd"}
    return inputs, request_data


@parametrize_with_cases("inputs,request_data", cases=case_does_not_depend_on_fixture, idstyle='explicit')
def test_create_no_fixture_idstyle_explicit(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_does_not_depend_on_fixture, ids=("custom{%i}" % i for i in itertools.count()))
def test_create_no_fixture_ids_generator(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_does_not_depend_on_fixture, ids=mygen)
def test_create_no_fixture_ids_callable(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_does_not_depend_on_fixture, idstyle="compact")
def test_create_no_fixture_idstyle_compact(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_does_not_depend_on_fixture)  # , idstyle="None"  # default
def test_create_no_fixture_idstyle_none(inputs, request_data):
    pass


def test_synthesis(module_results_dct):
    simple_id = "simple" if has_pytest_param else "simple[0]-simple[1]"

    lst = list(module_results_dct)
    if sys.version_info >= (3, 6):
        # the AUTO id gen uses dict iteration which has random order in old python
        assert lst[3] == 'test_create_fixture_ids_callable_str[(inputs,request_data)/P0F/simple]'

    assert lst[:3] + lst[4:] == [
        'test_create_fixture_idstyle_explicit[(inputs,request_data)/simple]',  # explicit
        'test_create_fixture_ids_generator[custom{0}]',
        "test_create_fixture_ids_callable[hello_simple]",
        'test_create_fixture_idstyle_compact[/simple]',    # compact
        'test_create_fixture_idstyle_none[simple]',     # none (default)
        'test_create_no_fixture_idstyle_explicit[%s]' % simple_id,  # explicit: not taken into account
        'test_create_no_fixture_ids_generator[custom{0}]',
        "test_create_no_fixture_ids_callable[hello_simple]",
        'test_create_no_fixture_idstyle_compact[%s]' % simple_id,  # compact: not taken into account
        'test_create_no_fixture_idstyle_none[%s]' % simple_id,  # none: not taken into account
    ]
