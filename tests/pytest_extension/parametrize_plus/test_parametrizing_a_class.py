# This checks for issue 215 https://github.com/smarie/python-pytest-cases/issues/215
import pytest

from pytest_cases import parametrize, fixture


@parametrize(foo=("bar",))
class TestFoo:
    def test_foo(self, foo):
        pass


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        "test_foo[foo=bar]"
    ]


@fixture
def a():
    return


def test_fixture_refs_are_not_supported_when_decorating_classes():
    class TestCls:
        pass

    with pytest.raises(NotImplementedError) as e:
        parametrize(foo=("bar", a))(TestCls)

    assert str(e.value).startswith("@parametrize can not be used to decorate a Test class")
