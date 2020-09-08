# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE
from pytest_steps import test_steps, StepsDataHolder
try:  # python 3.5+
    from pytest_cases import CaseData
except ImportError:
    pass


def case_simple(step_name):
    # type: (str) -> CaseData
    """ First case.
    This function is called for each test step, we make the case data output vary accordingly"""
    
    ins = dict(a=1, b=2)

    if step_name == 'step_check_a':
        outs = 2, 3
    elif step_name == 'step_check_b':
        outs = 5, 4
    else:
        raise ValueError("Unknown step")

    return ins, outs, None


def case_simple2(step_name):
    # type: (str) -> CaseData
    """ Second case.
    This function is called for each test step, we make the case data output vary accordingly"""
    ins = dict(a=-1, b=2)

    if step_name == 'step_check_a':
        outs = 0, 3
    elif step_name == 'step_check_b':
        outs = 1, 4
    else:
        raise ValueError("Unknown step")

    return ins, outs, None


def step_check_a(test_data,  # type: StepsDataHolder
                 ins, expected_o, expected_e):
    """ Step a of the test """

    # Use the three items as usual
    print(ins)
    
    # A new 
    assert not hasattr(test_data, 'ins')
    test_data.ins = ins


def step_check_b(test_data,  # type: StepsDataHolder
                 ins, expected_o, expected_e):
    """ Step b of the test """

    # Use the three items as usual
    print(test_data.ins)


@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite_parametrized_cases(test_step,
                                  case_data,  # type: CaseDataGetter
                                  steps_data  # type: StepsDataHolder
                                  ):

    # Get the data for this particular case
    ins, expected_o, expected_e = case_data.get(test_step.__name__)

    # Execute the step
    test_step(steps_data, ins, expected_o, expected_e)
