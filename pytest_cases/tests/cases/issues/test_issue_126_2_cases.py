# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize


def case_a(b, a):
    """
    Return the case of two strings.

    Args:
        b: (todo): write your description
        a: (todo): write your description
    """
    # a and b are fixtures defined in caller module/class
    # note that case id is also 'a'. The goal is to check that no conflict happens here
    assert a in (1, 2)
    assert b == -1
    return 'case!'


@parametrize(a=('*', '**'))
def case_b(b, a):
    """
    Return the case of two case.

    Args:
        b: (todo): write your description
        a: (todo): write your description
    """
    assert b == -1
    assert a in ('*', '**')
    return 'case!'


class CaseA:
    def case_a(self, b, a):
        """
        Case case case of two strings.

        Args:
            self: (todo): write your description
            b: (todo): write your description
            a: (todo): write your description
        """
        # a and b are fixtures defined in caller module/class
        # note that case id is also 'a'. The goal is to check that no conflict happens here
        assert a in (1, 2)
        assert b == -1
        return 'case!'

    @parametrize(a=('*', '**'))
    def case_b(self, b, a):
        """
        Returns the case of two case.

        Args:
            self: (todo): write your description
            b: (todo): write your description
            a: (todo): write your description
        """
        assert b == -1
        assert a in ('*', '**')
        return 'case!'
