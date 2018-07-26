from inspect import signature
from itertools import product

import pytest


class ResultsHolder:
    """
    An object that is passed along the various steps of your tests.
    You can put intermediate results in here, and find them in the following steps.

    Note: you can use `vars(results)` to see the available results.
    """
    pass


def test_steps(*steps, test_step_argname: str='test_step', test_results_argname: str='results'):
    """
    Decorates a test function so as to automatically parametrize it with all steps listed as arguments.

    When the steps are functions, this is equivalent to
    @pytest.mark.parametrize(test_step_argname, steps, ids=lambda x: x.__name__)

    :param steps:
    :return:
    """
    def steps_decorator(test_func):
        """
        The generated test function decorator.

        It is equivalent to @mark.parametrize('case_data', cases) where cases is a tuple containing a CaseDataGetter for
        all case generator functions

        :param test_func:
        :return:
        """
        def get_id(f):
            if callable(f) and hasattr(f, '__name__'):
                return f.__name__
            else:
                return str(f)

        step_ids = [get_id(f) for f in steps]

        # Finally create the pytest decorator and apply it
        # depending on the presence of test_results_argname in signature
        s = signature(test_func)
        if test_results_argname in s.parameters:
            # create a results holder
            result = ResultsHolder()  # TODO use Munch or MaxiMunch from `mixture` project, when publicly available ?
            steps_and_result = product(steps, (result, ))
            parametrizer = pytest.mark.parametrize(test_step_argname + ',' + test_results_argname, steps_and_result,
                                                   ids=step_ids)
        else:
            parametrizer = pytest.mark.parametrize(test_step_argname, steps, ids=step_ids)

        return parametrizer(test_func)

    return steps_decorator


test_steps.__test__ = False  # to prevent pytest to think that this is a test !
