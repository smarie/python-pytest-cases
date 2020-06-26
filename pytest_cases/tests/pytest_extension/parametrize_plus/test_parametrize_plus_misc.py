import pytest

from pytest_cases import parametrize_plus


def test_argname_error():
    with pytest.raises(ValueError, match="parameter 'a' not found in test function signature"):
        @parametrize_plus("a", [True])
        def test_foo(b):
            pass
