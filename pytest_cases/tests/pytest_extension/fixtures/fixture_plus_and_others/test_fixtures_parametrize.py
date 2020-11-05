# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
import pytest
from pytest_cases import pytest_fixture_plus


has_pytest_param = hasattr(pytest, 'param')


@pytest_fixture_plus(scope="module")
@pytest.mark.parametrize("arg1", ["one", "two"])
@pytest.mark.parametrize("arg2", ["one", "two"])
def myfix(arg1, arg2):
    """
    Return the two arguments arg1 and arg2.

    Args:
        arg1: (todo): write your description
        arg2: (str): write your description
    """
    return arg1, arg2


def test_one(myfix):
    """
    Test the test test

    Args:
        myfix: (str): write your description
    """
    assert myfix[0] in {"one", "two"}
    assert myfix[1] in {"one", "two"}
    print(myfix)


def test_synthesis(module_results_dct):
    """Use pytest-harvest to check that the list of executed tests is correct """

    assert list(module_results_dct) == ['test_one[one-one]',
                                        'test_one[one-two]',
                                        'test_one[two-one]',
                                        'test_one[two-two]']


# pytest.param - not available in all versions
if not has_pytest_param:
    # with pytest < 3.2.0 we
    # - would have to merge all parametrize marks if we wish to pass a kwarg (here, ids)
    # - cannot use pytest.param as it is not taken into account
    # > no go

    def test_warning_pytest2():
        """
        Evaluate python 2.

        Args:
        """
        with pytest.raises(ValueError) as exc_info:
            @pytest_fixture_plus
            @pytest.mark.parametrize("arg2", [0], ids=str)
            @pytest.mark.parametrize("arg1", [1])
            def a(arg1, arg2):
                """
                Compute the difference between two arguments.

                Args:
                    arg1: (todo): write your description
                    arg2: (str): write your description
                """
                return arg1, arg2
        assert "Unfortunately with this old pytest version it" in str(exc_info.value)

else:
    @pytest_fixture_plus
    @pytest.mark.parametrize("arg3", [pytest.param(0, id='!0!')], ids=str)
    @pytest.mark.parametrize("arg1, arg2", [
        (1, 2),
        pytest.param(3, 4, id="p_a"),
        pytest.param(5, 6, id="skipped", marks=pytest.mark.skip)
    ])
    def myfix2(arg1, arg2, arg3):
        """
        Fixme : class : two arguments.

        Args:
            arg1: (todo): write your description
            arg2: (str): write your description
            arg3: (str): write your description
        """
        return arg1, arg2, arg3


    def test_two(myfix2):
        """
        Test if two two integers

        Args:
            myfix2: (str): write your description
        """
        assert myfix2 in {(1, 2, 0), (3, 4, 0), (5, 6, 0)}
        print(myfix2)


    @pytest_fixture_plus
    @pytest.mark.parametrize("arg1, arg2", [
        pytest.param(5, 6, id="a")
    ], ids=['ignored_id'])
    def myfix3(arg1, arg2):
        """
        Fixme : pyfix3fix.

        Args:
            arg1: (todo): write your description
            arg2: (str): write your description
        """
        return arg1, arg2


    def test_three(myfix2, myfix3):
        """
        Test if the test

        Args:
            myfix2: (str): write your description
            myfix3: (str): write your description
        """
        assert myfix2 in {(1, 2, 0), (3, 4, 0), (5, 6, 0)}
        print(myfix2)


    def test_synthesis(module_results_dct):
        """Use pytest-harvest to check that the list of executed tests is correct """

        assert list(module_results_dct) == ['test_one[one-one]',
                                            'test_one[one-two]',
                                            'test_one[two-one]',
                                            'test_one[two-two]',
                                            'test_two[1-2-!0!]',
                                            'test_two[p_a-!0!]',
                                            'test_three[1-2-!0!-a]',
                                            'test_three[p_a-!0!-a]']