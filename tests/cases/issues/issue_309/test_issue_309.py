
import pytest


def test_get_all_cases_auto_raises(get_all_cases_auto_fails):
    with pytest.raises(ValueError):
        get_all_cases_auto_fails()
