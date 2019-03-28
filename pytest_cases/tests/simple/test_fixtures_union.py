import pytest
from pytest_cases import pytest_parametrize_plus, fixture_union


@pytest.fixture(params=[2, 3])
def a():
    return 'a123'


@pytest.fixture(params=[0, 1, 2])
def b():
    return 'b321'


# @pytest.fixture
# def c(a, b, request):
#     return request


f_union = fixture_union("f_union", a, "b")


def test_fixture_union(f_union):
    return

# @pytest.fixture
# def getfixture(request):
#     def _getfixture(name):
#         return request.getfixturevalue(name)
#     return _getfixture
#
#
# @pytest_parametrize_plus('_fixture, expect', fixtures=[a, b])
# def test_foo(_fixture, expected):
#     assert _fixture == expected
