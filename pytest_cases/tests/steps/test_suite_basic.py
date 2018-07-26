from pytest_cases import test_steps, ResultsHolder


def step_a():
    """ Step a of the test """

    # perform this step
    print("step a")
    assert not False


def step_b():
    """ Step b of the test """

    # perform this step
    print("step b")
    assert not False


# equivalent to
# @pytest.mark.parametrize('test_step', (step_check_a, step_check_b), ids=lambda x: x.__name__)
@test_steps(step_a, step_b)
def test_suite_no_results(test_step):
    """ """

    # Execute the step
    test_step()


def step_a(results: ResultsHolder):
    """ Step a of the test """

    # perform this step
    print("step a")
    assert not False

    # intermediate results can be stored in results
    results.intermediate_a = 'some intermediate result created in step a'


def step_b(results: ResultsHolder):
    """ Step b of the test """

    # perform this step
    print("step b")
    new_text = results.intermediate_a + " ... augmented"
    print(new_text)
    assert len(new_text) == 56


# equivalent to
# @pytest.mark.parametrize('test_step', ((step_check_a, results), (step_check_b, results)), ids=['step_check_a', 'step_check_b'])
@test_steps(step_a, step_b)
def test_suite_with_results(test_step, results: ResultsHolder):
    """ """

    # Execute the step
    test_step(results)
