# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest

from pytest_cases import assert_exception


def test_assert_exception():
    # good type
    with assert_exception(ValueError):
        raise ValueError()

    # good type - inherited
    class MyErr(ValueError):
        pass
    with assert_exception(ValueError):
        raise MyErr()

    # no exception
    with pytest.raises(AssertionError, match="DID NOT RAISE any BaseException"):
        with assert_exception(ValueError):
            pass

    # wrong type
    with pytest.raises(AssertionError, match=r"Caught exception TypeError\(\) "
                                             "is not an instance of expected type.*ValueError"):
        with assert_exception(ValueError):
            raise TypeError()

    # good repr pattern
    with assert_exception(r"ValueError\('hello'[,]?\)"):
        raise ValueError("hello")

    # good instance - equality check
    class MyExc(Exception):
        def __eq__(self, other):
            return vars(self) == vars(other)

    with assert_exception(MyExc('hello')):
        raise MyExc("hello")

    # good equality but wrong type
    with pytest.raises(AssertionError, match=r"is not an instance of expected type.*MyExc"):
        with assert_exception(MyExc('hello')):
            raise Exception("hello")
