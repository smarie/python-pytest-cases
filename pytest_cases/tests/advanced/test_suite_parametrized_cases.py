from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, CaseData
from pytest_steps import test_steps, StepsDataHolder


def case_simple(step_name: str) -> CaseData:
    """ First case.
    This function is called for each test step, we make the case data output vary accordingly"""
    
    ins = dict(a=1, b=2)

    if step_name is 'step_check_a':
        outs = 2, 3
    elif step_name is 'step_check_b':
        outs = 5, 4
    else:
        raise ValueError("Unknown step")

    return ins, outs, None


def case_simple2(step_name: str) -> CaseData:
    """ Second case.
    This function is called for each test step, we make the case data output vary accordingly"""
    ins = dict(a=-1, b=2)

    if step_name is 'step_check_a':
        outs = 0, 3
    elif step_name is 'step_check_b':
        outs = 1, 4
    else:
        raise ValueError("Unknown step")

    return ins, outs, None


def step_check_a(test_data: StepsDataHolder, ins, expected_o, expected_e):
    """ Step a of the test """

    # Use the three items as usual
    print(ins)
    
    # A new 
    assert not hasattr(test_data, 'ins')
    test_data.ins = ins


def step_check_b(test_data, ins, expected_o, expected_e):
    """ Step b of the test """

    # Use the three items as usual
    print(test_data.ins)


@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite_parametrized_cases(test_step, case_data: CaseDataGetter, steps_data: StepsDataHolder):

    # Get the data for this particular case
    ins, expected_o, expected_e = case_data.get(test_step.__name__)

    # Execute the step
    test_step(steps_data, ins, expected_o, expected_e)
