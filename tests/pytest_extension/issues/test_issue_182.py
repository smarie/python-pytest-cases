import pytest
from pytest_cases import fixture


class TestMethod:
    @pytest.fixture
    def pytest_fxt(self):
        return "Hello"

    def test_with_pytest(self, pytest_fxt):
        # succeeds
        assert pytest_fxt == "Hello"

    @fixture
    def cases_fxt(self):
        return "Hello"

    def test_with_cases(self, cases_fxt):
        # raises an error with regards to 'self'
        assert cases_fxt == "Hello"


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_with_pytest',
        'test_with_cases'
    ]
