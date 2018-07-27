from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE, cases_generator


# @lru_cache(maxsize=3)
@cases_generator("case {i}", i=range(3), lru_cache=True)
def case_gen(i) -> CaseData:
    print("generating case " + str(i))
    ins = i
    outs, err = None, None
    return ins, outs, err


@cases_data(module=THIS_MODULE)
def test_a(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    print(i)


@cases_data(module=THIS_MODULE)
def test_b(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    print(i)
