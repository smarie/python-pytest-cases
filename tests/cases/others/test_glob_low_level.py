from pytest_cases import case

from pytest_cases.case_parametrizer_new import create_glob_name_filter


def test_glob_low_level():
    """Tests that the glob-like filtering mechanism for case ids works"""

    def case_fun_with_id(id):
        @case(id=id)
        def _f():
            pass
        return _f

    filtr = create_glob_name_filter("o*_success")
    assert filtr(case_fun_with_id("oooh_success"))
    assert not filtr(case_fun_with_id("oh_no"))
    # beginning and end: no match
    assert not filtr(case_fun_with_id("oh_success2"))
    assert not filtr(case_fun_with_id("yoh_success"))

    filtr = create_glob_name_filter("*_*")
    assert filtr(case_fun_with_id("oh_success"))
    assert filtr(case_fun_with_id("oh_no"))
    assert not filtr(case_fun_with_id("ohno"))

    filtr = create_glob_name_filter("*_$[ab]+")
    assert filtr(case_fun_with_id("oh_$[ab]+"))
    assert not filtr(case_fun_with_id("oh_$"))
