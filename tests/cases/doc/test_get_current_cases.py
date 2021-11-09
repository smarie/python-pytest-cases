# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>
from pytest_cases import parametrize_with_cases, fixture, case, filters, get_current_cases
from . import test_get_current_cases_cases as casesfile

from pytest_cases.common_pytest_marks import PYTEST3_OR_GREATER


@case(tags=("no_fix_needed",))
def case_a():
    return 1, 2


@case(tags=("no_fix_needed",))
def case_b():
    return 1, 2


@case(id="custom_id", tags=("no_fix_needed",))
def tuplecase_a():
    return 1, 2


@case(id="custom_id")
def case_a_fixture(request):
    return 1, 2


def tuplecase_a_fixture(request):
    return 1, 2


@parametrize_with_cases("withfixrefs_f1,withfixrefs_f2", cases=".", prefix="tuplecase_")
@parametrize_with_cases("withfixrefs_f", cases=".", prefix="case_")
@parametrize_with_cases("purelazy_t1,purelazy_t2", cases=".", prefix="tuplecase_", filter=filters.has_tags("no_fix_needed"))
@parametrize_with_cases("purelazy_a", cases=".", prefix="case_", filter=filters.has_tags("no_fix_needed"))
def test_local_cases(purelazy_a, purelazy_t1, purelazy_t2, withfixrefs_f, withfixrefs_f1, withfixrefs_f2,
                     current_cases, request):

    # also try with a late call, just to be sure that a cache would not prevent us to access the lazy value getters
    late_call_dct = get_current_cases(request)
    for cases_dct in (current_cases, late_call_dct):
        assert set(cases_dct.keys()) == {
            "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2"
        }
        _assert_cases(cases_dct, local=True)


@parametrize_with_cases("withfixrefs_f1,withfixrefs_f2", prefix="tuplecase_")
@parametrize_with_cases("withfixrefs_f", prefix="case_")
@parametrize_with_cases("purelazy_t1,purelazy_t2", prefix="tuplecase_", filter=filters.has_tags("no_fix_needed"))
@parametrize_with_cases("purelazy_a", prefix="case_", filter=filters.has_tags("no_fix_needed"))
def test_separate_cases_file(purelazy_a, purelazy_t1, purelazy_t2, withfixrefs_f, withfixrefs_f1, withfixrefs_f2,
                             current_cases, request):

    # also try with a late call, just to be sure that a cache would not prevent us to access the lazy value getters
    late_call_dct = get_current_cases(request)
    for cases_dct in (current_cases, late_call_dct):
        assert set(cases_dct.keys()) == {
            "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2"
        }
        _assert_cases(cases_dct, local=False)


def _assert_cases(current_cases, local=True):
    ref_dict = {
        'a': case_a if local else casesfile.case_a,
        'b': case_b if local else casesfile.case_b
    }
    assert len(current_cases["purelazy_a"]) == 3
    assert current_cases["purelazy_a"][1] is ref_dict[current_cases["purelazy_a"][0]]
    assert current_cases["purelazy_a"][2] == {}

    assert len(current_cases["purelazy_t1"]) == 3
    assert current_cases["purelazy_t1"][0] == "custom_id"
    assert current_cases["purelazy_t1"][1] is (tuplecase_a if local else casesfile.tuplecase_a)
    assert current_cases["purelazy_t1"][2] == {}
    assert current_cases["purelazy_t1"] == current_cases["purelazy_t2"]

    ref_dict = {
        'a': case_a if local else casesfile.case_a,
        'b': case_b if local else casesfile.case_b,
        'custom_id': case_a_fixture if local else casesfile.case_a_fixture
    }
    assert len(current_cases["withfixrefs_f"]) == 3
    assert current_cases["withfixrefs_f"][1] is ref_dict[current_cases["withfixrefs_f"][0]]
    assert current_cases["withfixrefs_f"][2] == {}

    ref_dict = {
        'custom_id': tuplecase_a if local else casesfile.tuplecase_a,
        "a_fixture": tuplecase_a_fixture if local else casesfile.tuplecase_a_fixture
    }
    assert len(current_cases["withfixrefs_f1"]) == 3
    assert current_cases["withfixrefs_f1"][1] is ref_dict[current_cases["withfixrefs_f1"][0]]
    assert current_cases["withfixrefs_f2"] == current_cases["withfixrefs_f1"]


if PYTEST3_OR_GREATER:
    @fixture
    @parametrize_with_cases("purelazy_t1,purelazy_t2", cases=".", prefix="tuplecase_", filter=filters.has_tags("no_fix_needed"))
    @parametrize_with_cases("withfixrefs_f1,withfixrefs_f2", cases=".", prefix="tuplecase_")
    @parametrize_with_cases("purelazy_a", cases=".", prefix="case_", filter=filters.has_tags("no_fix_needed"))
    @parametrize_with_cases("withfixrefs_f", cases=".", prefix="case_")
    def my_fixture_local(purelazy_a, purelazy_t1, purelazy_t2, withfixrefs_f, withfixrefs_f1, withfixrefs_f2, current_cases, request):
        late_call_dct = get_current_cases(request)
        for cases_dct in (current_cases, late_call_dct):
            assert set(cases_dct.keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2",
                # NEW: the fixture
                "my_fixture_local"
            }
            _assert_cases(cases_dct, local=True)
            assert set(cases_dct["my_fixture_local"].keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2"
            }
            _assert_cases(cases_dct["my_fixture_local"], local=True)


    @fixture
    @parametrize_with_cases("withfixrefs_f1,withfixrefs_f2", prefix="tuplecase_")
    @parametrize_with_cases("withfixrefs_f", prefix="case_")
    @parametrize_with_cases("purelazy_t1,purelazy_t2", prefix="tuplecase_", filter=filters.has_tags("no_fix_needed"))
    @parametrize_with_cases("purelazy_a", prefix="case_", filter=filters.has_tags("no_fix_needed"))
    def my_fixture_separate_file(purelazy_a, purelazy_t1, purelazy_t2, withfixrefs_f, withfixrefs_f1, withfixrefs_f2, current_cases, request):
        late_call_dct = get_current_cases(request)
        for cases_dct in (current_cases, late_call_dct):
            assert set(cases_dct.keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2",
                # NEW: the fixture
                "my_fixture_separate_file"
            }
            _assert_cases(cases_dct, local=False)
            assert set(cases_dct["my_fixture_separate_file"].keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2"
            }
            _assert_cases(cases_dct["my_fixture_separate_file"], local=False)


    @parametrize_with_cases("withfixrefs_f1,withfixrefs_f2", cases=".", prefix="tuplecase_")
    @parametrize_with_cases("withfixrefs_f", cases=".", prefix="case_")
    @parametrize_with_cases("purelazy_t1,purelazy_t2", cases=".", prefix="tuplecase_", filter=filters.has_tags("no_fix_needed"))
    @parametrize_with_cases("purelazy_a", cases=".", prefix="case_", filter=filters.has_tags("no_fix_needed"))
    def test_local_cases_with_fix(purelazy_a, purelazy_t1, purelazy_t2, withfixrefs_f, withfixrefs_f1, withfixrefs_f2, my_fixture_local, current_cases, request):
        late_call_dct = get_current_cases(request)
        for cases_dct in (current_cases, late_call_dct):
            assert set(cases_dct.keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2",
                # NEW: the fixture
                "my_fixture_local"
            }
            _assert_cases(cases_dct, local=True)
            assert set(cases_dct["my_fixture_local"].keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2"
            }
            _assert_cases(cases_dct["my_fixture_local"], local=True)


    @parametrize_with_cases("withfixrefs_f1,withfixrefs_f2", prefix="tuplecase_")
    @parametrize_with_cases("withfixrefs_f", prefix="case_")
    @parametrize_with_cases("purelazy_t1,purelazy_t2", prefix="tuplecase_", filter=filters.has_tags("no_fix_needed"))
    @parametrize_with_cases("purelazy_a", prefix="case_", filter=filters.has_tags("no_fix_needed"))
    def test_separate_cases_file_with_fix(purelazy_a, purelazy_t1, purelazy_t2, withfixrefs_f, withfixrefs_f1, withfixrefs_f2, my_fixture_separate_file, current_cases, request):
        late_call_dct = get_current_cases(request)
        for cases_dct in (current_cases, late_call_dct):
            assert set(cases_dct.keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2",
                # NEW: the fixture
                "my_fixture_separate_file"
            }
            _assert_cases(cases_dct, local=False)
            assert set(cases_dct["my_fixture_separate_file"].keys()) == {
                "purelazy_a", "purelazy_t1", "purelazy_t2", "withfixrefs_f", "withfixrefs_f1", "withfixrefs_f2"
            }
            _assert_cases(cases_dct["my_fixture_separate_file"], local=False)
