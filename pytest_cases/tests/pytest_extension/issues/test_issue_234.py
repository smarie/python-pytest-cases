import pytest


@pytest.mark.parametrize(
    argnames="test_arg",
    argvalues=[1, 2, 3]
)
def test_keyword_paramz(test_arg):
    assert True
