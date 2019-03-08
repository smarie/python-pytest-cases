from pytest_cases.tests.example_code import super_function_i_want_to_test

from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, cases_generator
try:
    from pytest_cases import CaseData
except ImportError:
    pass


def case_simple():
    # type: (...) -> CaseData
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None


# We can not do something like this: it is not possible to know the number of cases in advance
# @cases_generator
# def case_simple_generator() -> CaseData:
#     for i in range(10):
#         ins = dict(a=i, b=i+1)
#         outs = i+1, i+2
#         yield ins, outs, None


@cases_generator("test with i={i}, j={j} and name template", i=range(2), j=range(3))
def case_simple_generator(i, j):
    # type: (...) -> CaseData
    ins = dict(a=i, b=j)
    outs = i+1, j+1
    return ins, outs, None


@cases_generator("test with i={i}, j={j} and names callable provider", i=range(2), j=range(3))
def case_simple_generator_callable_name(i, j):
    # type: (...) -> CaseData
    ins = dict(a=i, b=j)
    outs = i+1, j+1
    return ins, outs, None


names_list = ["test with i={i}, j={j} and explicit names list".format(i=i, j=j) for i in range(2) for j in range(3)]


@cases_generator(names_list, i=range(2), j=range(3))
def case_simple_generator_explicit_name_list(i, j):
    # type: (...) -> CaseData
    ins = dict(a=i, b=j)
    outs = i+1, j+1
    return ins, outs, None


@cases_data(module=THIS_MODULE)
def test_with_cases_decorated(case_data  # type: CaseDataGetter
                              ):

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = super_function_i_want_to_test(**i)
    assert outs == expected_o
