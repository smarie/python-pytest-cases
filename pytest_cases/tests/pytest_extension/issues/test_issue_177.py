import pytest

from pytest_cases.common_pytest_marks import has_pytest_param
from pytest_cases import fixture, parametrize


if has_pytest_param:
    @fixture
    def a():
       return "aaa"


    @fixture
    def b():
       return "bb"


    @parametrize("letters", [a,
                             pytest.param(b, id='hey'),
                             pytest.param(b, marks=pytest.mark.skip)])
    @parametrize("order", [True, False])
    @parametrize("no_auto", [b], auto_refs=False)
    @parametrize("explicit_auto", [a], auto_refs=True)
    def test_stuff(letters, order, no_auto, explicit_auto):
        assert no_auto == b
        assert explicit_auto == "aaa"
        if not order:
            letters = letters[::-1]
        assert letters.upper() == letters.lower().upper()


    @fixture
    def c():
       return "cc", True


    @parametrize("letters,order", [(a, True),
                                   pytest.param(b, False, id='hey'),
                                   pytest.param(b, "notused", marks=pytest.mark.skip),
                                   c,
                                   pytest.param(c, id='ho')
                                   ]
                 )
    @parametrize("no_auto,no_auto2", [(b, 'no')], auto_refs=False)
    @parametrize("explicit_auto,explicit_auto2", [(a, 'yes')], auto_refs=True)
    def test_stuff_multi(letters, order, no_auto, no_auto2, explicit_auto, explicit_auto2):
        assert no_auto, no_auto2 == (b, 'no')
        assert explicit_auto, explicit_auto2 == ("aaa", "yes")
        if not order:
            letters = letters[::-1]
        assert letters.upper() == letters.lower().upper()


    def test_synthesis(module_results_dct):
        assert list(module_results_dct) == [
            'test_stuff[a-b-True-a]',
            'test_stuff[a-b-False-a]',
            'test_stuff[hey-b-True-a]',
            'test_stuff[hey-b-False-a]',
            'test_stuff_multi[a-True-b-no-a-yes]',
            'test_stuff_multi[hey-b-no-a-yes]',
            'test_stuff_multi[c-b-no-a-yes]',
            'test_stuff_multi[ho-b-no-a-yes]'
        ]
