# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE
from pytest_steps import test_steps, StepsDataHolder
try:  # python 3.5+
    from pytest_cases import MultipleStepsCaseData
except ImportError:
    pass


def case_simple():
    # type: () -> MultipleStepsCaseData
    ins = dict(a=1, b=2)

    outs_for_a = 2, 3
    outs_for_b = 5, 4
    outs = dict(step_check_a=outs_for_a, step_check_b=outs_for_b)

    return ins, outs, None


def case_simple2():
    # type: () -> MultipleStepsCaseData
    ins = dict(a=-1, b=2)

    outs_for_a = 2, 3
    outs_for_b = 5, 4
    outs = dict(step_check_a=outs_for_a, step_check_b=outs_for_b)

    return ins, outs, None


def step_check_a(test_data, ins, expected_o, expected_e):
    """ Step a of the test """

    # Use the three items as usual
    print(ins)
    assert not hasattr(test_data, 'ins')
    test_data.ins = ins


def step_check_b(test_data, ins, expected_o, expected_e):
    """ Step b of the test """

    # Use the three items as usual
    print(test_data.ins)


# equivalent to @pytest.mark.parametrize('test_step', (step_check_a, step_check_b), ids=lambda x: x.__name__)
@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite_shared_dict_cases(test_step,
                                 case_data,  # type: CaseDataGetter
                                 steps_data  # type: StepsDataHolder
                                 ):
    """ """

    # Get the data
    ins, expected_o, expected_e = case_data.get()

    # Filter it based on the step
    key = test_step.__name__
    expected_o = None if expected_o is None else expected_o[key]
    expected_e = None if expected_e is None else expected_e[key]

    # Execute the step
    test_step(steps_data, ins, expected_o, expected_e)
