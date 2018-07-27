from pytest_cases import test_steps, cases_data, CaseDataGetter, THIS_MODULE, CaseData, ResultsHolder


def case_simple(step_name: str) -> CaseData:
    ins = dict(a=1, b=2)

    if step_name is 'step_check_a':
        outs = 2, 3
    elif step_name is 'step_check_b':
        outs = 5, 4
    else:
        raise ValueError("Unknown step")

    return ins, outs, None


def case_simple2(step_name: str) -> CaseData:
    ins = dict(a=-1, b=2)

    if step_name is 'step_check_a':
        outs = 0, 3
    elif step_name is 'step_check_b':
        outs = 1, 4
    else:
        raise ValueError("Unknown step")

    return ins, outs, None


def step_check_a(storage, ins, expected_o, expected_e):
    """ Step a of the test """

    # Use the three items as usual
    print(ins)
    assert not hasattr(storage, 'ins')
    storage.ins = ins


def step_check_b(storage, ins, expected_o, expected_e):
    """ Step b of the test """

    # Use the three items as usual
    print(storage.ins)


# equivalent to @pytest.mark.parametrize('test_step', (step_check_a, step_check_b), ids=lambda x: x.__name__)
@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite_parametrized_cases(test_step, case_data: CaseDataGetter, results: ResultsHolder):

    # Get the data for this particular case
    ins, expected_o, expected_e = case_data.get(test_step.__name__)

    # Execute the step
    test_step(results, ins, expected_o, expected_e)
