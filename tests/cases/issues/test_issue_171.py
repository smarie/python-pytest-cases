import pytest

from pytest_cases.common_pytest_marks import has_pytest_param
from pytest_cases import case, parametrize_with_cases, fixture


class CreateCases(object):
    @case(id="current_object")
    def case_create_1(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="lala")
    def case_create_10(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="without_validation")
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

    @case(id="xml_with_namespaces")
    def case_create_4(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="duplicate_name")
    def case_create_6(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="duplicate_name_without_valid")
    @pytest.mark.usefixtures("validationOff")
    def case_create_61(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="not_enough_namespaceses")
    def case_create_7(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data


    @case(id="invalid_xml")
    def case_create_8(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="invalid_xml_without_valid")
    @pytest.mark.usefixtures("validationOff")
    def case_create_9(self):
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data


@fixture
def validationOff():
    # app.config["validation"] = False
    yield
    # app.config["validation"] = True


@parametrize_with_cases("inputs,request_data", cases=".", prefix="case_create_")
def test_create(inputs, request_data):
    pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
         'test_create[current_object]',
         'test_create[lala]',
         'test_create[%swithout_validation]' % ("" if has_pytest_param else "1"),
         'test_create[history_object]',
         'test_create[xml_with_namespaces]',
         'test_create[duplicate_name]',
         'test_create[%sduplicate_name_without_valid]' % ("" if has_pytest_param else "3"),
         'test_create[not_enough_namespaceses]',
         'test_create[invalid_xml]',
         'test_create[%sinvalid_xml_without_valid]' % ("" if has_pytest_param else "5"),
    ]
