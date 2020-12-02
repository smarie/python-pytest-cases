import sys

import itertools

import pytest
from pytest_cases.common_pytest_marks import has_pytest_param

from pytest_cases import parametrize_with_cases, case, AUTO


@pytest.fixture
def barToFoo():
    pass


@case(id="simple")
def case_create_2(barToFoo):
    inputs = ["foo", "bar"]
    request_data = {"foo": "dfg", "data": "asd"}
    return inputs, request_data


@parametrize_with_cases("inputs,request_data", cases=case_create_2)  # idstyle='explicit' by default
def test_create_fixture(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_2, ids=("custom{%i}" % i for i in itertools.count()))
def test_create_fixture_alt_id1(inputs, request_data):
    pass


def mygen(**kwargs):
    # sort alphabetically to preserve order on continuous integration builds
    return "hello_%s" % "_".join("%s=%s" % (k, kwargs[k]) for k in sorted(kwargs.keys()))


@parametrize_with_cases("inputs,request_data", cases=case_create_2, idgen=mygen)
def test_create_fixture_alt_id2(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_2, idgen=AUTO)
def test_create_fixture_alt_id2bis(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_2, idstyle="compact")
def test_create_fixture_alt_id3(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_2, idstyle=None)
def test_create_fixture_alt_id4(inputs, request_data):
    pass


@case(id="simple")
def case_create_3():
    inputs = ["foo", "bar"]
    request_data = {"foo": "dfg", "data": "asd"}
    return inputs, request_data


@parametrize_with_cases("inputs,request_data", cases=case_create_3)  # idstyle='explicit'
def test_create_no_fixture(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_3, ids=("custom{%i}" % i for i in itertools.count()))
def test_create_no_fixture_alt_id1(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_3, idgen=mygen)
def test_create_no_fixture_alt_id2(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_3, idstyle="compact")
def test_create_no_fixture_alt_id3(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_3, idstyle="None")
def test_create_no_fixture_alt_id4(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=case_create_3, idstyle="explicit")
def test_create_no_fixture_alt_id5(inputs, request_data):
    pass


def test_synthesis(module_results_dct):
    simple_id = "simple" if has_pytest_param else "simple[0]-simple[1]"

    lst = list(module_results_dct)
    if sys.version_info >= (3, 6):
        # the AUTO id gen uses dict iteration which has random order in old python
        assert lst[3] == 'test_create_fixture_alt_id2bis' \
                         '[inputs=fixture_ref<simple>[0]-request_data=fixture_ref<simple>[1]]'

    assert lst[:3] + lst[4:] == [
        'test_create_fixture[inputs_request_data_is_simple]',  # explicit (default)
        'test_create_fixture_alt_id1[custom{0}]',
        "test_create_fixture_alt_id2[hello_inputs=fixture_ref<simple>[0]_request_data=fixture_ref<simple>[1]]",
        'test_create_fixture_alt_id3[Psimple]',    # compact
        'test_create_fixture_alt_id4[simple]',     # none
        'test_create_no_fixture[%s]' % simple_id,  # explicit (default)
        'test_create_no_fixture_alt_id1[custom{0}]',
        "test_create_no_fixture_alt_id2[hello_inputs=simple[0]_request_data=simple[1]]",
        'test_create_no_fixture_alt_id3[%s]' % simple_id,  # compact
        'test_create_no_fixture_alt_id4[%s]' % simple_id,  # none
        'test_create_no_fixture_alt_id5[%s]' % simple_id   # explicit
    ]
