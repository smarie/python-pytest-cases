import pytest
from pytest_cases import case, parametrize_with_cases, fixture, parametrize


@pytest.fixture
def validationOff():
    return


@fixture
@parametrize("a", [0])
def validationOff2params(a):
    return


class CreateCases(object):
    @case(id="current_object")
    def case_create_1(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="not_valid")
    @pytest.mark.usefixtures("validationOff")
    def case_create_2(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="history_object")
    def case_create_3(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="xml_without_need_namespace")
    def case_create_4(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="xml_without_need_namespace_not_valid")
    @pytest.mark.usefixtures("validationOff2params")
    def case_create_6(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="xml_without_need_name")
    def case_create_7(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="xml_without_need_name_not_valid")
    @pytest.mark.usefixtures("validationOff")
    def case_create_8(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="xml_invalid")
    def case_create_9(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data


@parametrize_with_cases("inputs,request_data", cases=CreateCases)
def test_create_idstyle_explicit(inputs, request_data):
    pass


@parametrize_with_cases("inputs,request_data", cases=CreateCases, idstyle=None)
def test_create_idstyle_none(inputs, request_data):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [

    ]
