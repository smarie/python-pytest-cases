import pytest
from pytest_cases import fixture, parametrize


@pytest.fixture
def __my_repeat_step_number(request):
    return request.param


@pytest.hookimpl(trylast=True)
def pytest_generate_tests(metafunc):
    """This hook and fixture above are similar to what happens in pytest-repeat.
    See https://github.com/smarie/python-pytest-cases/issues/269
    """
    metafunc.fixturenames.append("__my_repeat_step_number")

    def make_progress_id(i, n=2):
        return '{0}-{1}'.format(i + 1, n)

    scope = metafunc.config.option.repeat_scope
    metafunc.parametrize(
        '__my_repeat_step_number',
        range(2),
        indirect=True,
        ids=make_progress_id,
        scope=scope
    )


@fixture
def my_fix():
    return 2


@parametrize("arg", (my_fix,))
def test_repeat(arg):
    assert arg == 2


def test_synthesis(module_results_dct):
    """Make sure that two tests were created."""
    assert list(module_results_dct) == [
        "test_repeat-1-2",
        "test_repeat-2-2"
    ]
