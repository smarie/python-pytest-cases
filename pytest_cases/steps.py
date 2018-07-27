from functools import lru_cache
from inspect import signature, getmodule

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
    `@pytest.mark.parametrize(test_step_argname, steps, ids=lambda x: x.__name__)`

    ```python
    from pytest_cases import test_steps

    def step_a():
        # perform this step
        print("step a")
        assert not False

    def step_b():
        # perform this step
        print("step b")
        assert not False

    @test_steps(step_a, step_b)
    def test_suite_no_results(test_step):
        # Execute the step
        test_step()
    ```

    You can add a 'results' parameter to your test function if you wish to share a `ResultsHolder` object between your
    steps.

    ```python
    def step_a(results: ResultsHolder):
        # perform this step
        print("step a")
        assert not False

        # intermediate results can be stored in results
        results.intermediate_a = 'some intermediate result created in step a'

    def step_b(results: ResultsHolder):
        # perform this step, leveraging the previous step's results
        print("step b")
        new_text = results.intermediate_a + " ... augmented"
        print(new_text)
        assert len(new_text) == 56

    @test_steps(step_a, step_b)
    def test_suite_with_results(test_step, results: ResultsHolder):
        # Execute the step with access to the results holder
        test_step(results)
    ```

    :param steps: a list of test steps. They can be anything, but typically they are non-test (not prefixed with 'test')
        functions.
    :param test_step_argname: the optional name of the function argument that will receive the test step object.
        Default is 'test_step'.
    :param test_results_argname: the optional name of the function argument that will receive the shared `ResultsHolder`
        object if present. Default is 'results'.
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
            # the user wishes to share results across test steps. Create a cached fixture
            @lru_cache(maxsize=None)
            def get_results_holder(**kwargs):
                """
                A factory for the ResultsHolder objects. Since it uses @lru_cache, the same ResultsHolder will be
                returned when the keyword arguments are the same.

                :param kwargs:
                :return:
                """
                return ResultsHolder()  # TODO use Munch or MaxiMunch from `mixture` project, when publicly available ?

            @pytest.fixture(name=test_results_argname)
            def results(request):
                """
                The fixture for the ResultsHolder. It implements an intelligent cache so that the same ResultsHolder
                object is used across test steps.

                :param request:
                :return:
                """
                # The object should be different everytime anything changes, except when the test step changes
                dont_change_when_these_change = {test_step_argname}

                # We also do not want the 'results' itself nor the pytest 'request' to be taken into account, since
                # the first is not yet defined and the second is an internal pytest variable
                dont_change_when_these_change.update({test_results_argname, 'request'})

                # List the values of all the test function parameters that matter
                kwargs = {argname: request.getfuncargvalue(argname)
                          for argname in request.funcargnames
                          if argname not in dont_change_when_these_change}

                # Get or create the cached Result holder for this combination of parameters
                return get_results_holder(**kwargs)

            # Add the fixture dynamically: we have to add it to the function holder module as explained in
            # https://github.com/pytest-dev/pytest/issues/2424
            module = getmodule(test_func)
            if test_results_argname not in dir(module):
                setattr(module, test_results_argname, results)
            else:
                raise ValueError("The {} fixture already exists in module {}: please specify a different "
                                 "`test_results_argname` in `@test_steps`".format(test_results_argname, module))

        # Finally parametrize the function with the test steps
        parametrizer = pytest.mark.parametrize(test_step_argname, steps, ids=step_ids)
        return parametrizer(test_func)

    return steps_decorator


test_steps.__test__ = False  # to prevent pytest to think that this is a test !
