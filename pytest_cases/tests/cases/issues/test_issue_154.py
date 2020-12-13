import pytest

from pytest_cases import case, parametrize_with_cases, fixture, parametrize, lazy_value, get_case_id


@pytest.fixture
def validationOff():
    return


@fixture
@parametrize("a", [0])
def validationOff2params(a):
    return


def foo():
    return "foo"


@pytest.mark.skip
def bar():
    assert False, "Should be skipped"


class CreateCases(object):
    @case(id="single")
    def case_single_param(self):
        """P0 Since the next case requires a fixture, this is a single param"""
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="fixref")
    @pytest.mark.usefixtures("validationOff")
    def case_implicit_fixture_ref(self):
        """F Requires a fixture"""
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="single_marked_skipped")
    @pytest.mark.skip
    def case_single_param_with_mark(self):
        """P2 Since the next case requires a fixture, this is a single param again"""
        assert False, "This should be skipped"

    @case(id="fixref_marked_skipped")
    @pytest.mark.usefixtures("validationOff")
    @pytest.mark.skip
    def case_implicit_fixture_ref_with_mark(self):
        """F Requires a fixture but is skipped"""
        assert False, "This should be skipped"

    @case(id="multi1")
    def case_multi_param(self):
        """P4:6"""
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="multi2_marked_skipped")
    @pytest.mark.skip
    def case_multi_param_with_mark(self):
        """P4:6 but this one should be skipped"""
        assert False, "Should be skipped"

    @case(id="fixref_target_is_parametrized")
    @pytest.mark.usefixtures("validationOff2params")
    def case_create_6(self):
        """F"""
        inputs = ["foo", "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="single_parametrized_lazy")
    @parametrize("o", [lazy_value(foo)])
    # we could use @pytest.mark.parametrize instead of @parametrize here since this is a fixture and has no marks in
    # the lazy value, but not recommended of course
    def case_create_7(self, o):
        """P7"""
        inputs = [o, "bar"]
        request_data = {"foo": "dfg", "data": "asd"}
        return inputs, request_data

    @case(id="fixref_target_is_parametrized_marked_skipped")
    @pytest.mark.skip
    @pytest.mark.usefixtures("validationOff2params")
    def case_create_8(self):
        """F"""
        assert False, "Should be skipped"

    @case(id="single_parametrized_lazy_value_target_is_skipped")
    @parametrize("o", [lazy_value(bar)])
    def case_create_9(self, o):
        """P9"""
        assert False, "Should be skipped"


def mygen(case_fun):
    return "M%s" % get_case_id(case_fun)


class TestTuples:
    @parametrize_with_cases("inputs,request_data", cases=CreateCases, idstyle="explicit")
    def test_create_tuple_idstyle_explicit(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}

    @parametrize_with_cases("inputs,request_data", cases=CreateCases, idstyle="compact")
    def test_create_tuple_idstyle_compact(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}

    @parametrize_with_cases("inputs,request_data", cases=CreateCases)  # , idstyle=None default
    def test_create_tuple_idstyle_none(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}

    @parametrize_with_cases("inputs,request_data", cases=CreateCases, idstyle=lambda o: "M%s" % o)
    def test_create_tuple_idstyle_mygen(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}

    @parametrize_with_cases("inputs,request_data", cases=CreateCases, ids=["%i" % i for i in range(10)])
    def test_create_tuple_ids_list(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}

    @parametrize_with_cases("inputs,request_data", cases=CreateCases, ids=["%i" % i for i in range(10)], idstyle="compact")
    def test_create_tuple_ids_list_style(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}

    @parametrize_with_cases("inputs,request_data", cases=CreateCases, ids=mygen)
    def test_create_tuple_ids_mygen(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}

    @parametrize_with_cases("inputs,request_data", cases=CreateCases, ids=mygen, idstyle="compact")
    def test_create_tuple_ids_mygen_style(self, inputs, request_data):
        assert inputs == ["foo", "bar"]
        assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases, idstyle="explicit")
def test_create_single_idstyle_explicit(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases, idstyle="compact")
def test_create_single_idstyle_compact(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases)  # , idstyle=None default
def test_create_single_idstyle_none(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases, idstyle=lambda o: "M%s" % o)
def test_create_single_idstyle_mygen(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases, ids=["%i" % i for i in range(10)])
def test_create_single_ids_list(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases, ids=["%i" % i for i in range(10)], idstyle="compact")
def test_create_single_ids_list_style(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases, ids=mygen)
def test_create_single_ids_mygen(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


@parametrize_with_cases("inputs_request_data", cases=CreateCases, ids=mygen, idstyle="compact")
def test_create_single_ids_mygen_style(inputs_request_data):
    inputs, request_data = inputs_request_data
    assert inputs == ["foo", "bar"]
    assert request_data == {"foo": "dfg", "data": "asd"}


def test_synthesis(module_results_dct):
    tuple_res = [
        # (1) explicit. Fixtures are created for all fixture refs, as well as for all consecutive groups of parameters
        # This idstyle is for debug. It should explicitly show how many fixture alternatives are created
        # and which of them are parametrized or not. Therefore the naming follows (<argnames>,)/<argvalue>
        # and for sequences of consecutive params we see P<from>:<to>-<argvalue>
        'test_create_tuple_idstyle_explicit[(inputs,request_data)/single]',
        'test_create_tuple_idstyle_explicit[(inputs,request_data)/fixref]',
        'test_create_tuple_idstyle_explicit[(inputs,request_data)/P4:6-multi1]',
        'test_create_tuple_idstyle_explicit[(inputs,request_data)/fixref_target_is_parametrized-0]',
        'test_create_tuple_idstyle_explicit[(inputs,request_data)/single_parametrized_lazy-foo]',
        # compact is like explicit but the argnames are dropped
        'test_create_tuple_idstyle_compact[/single]',
        'test_create_tuple_idstyle_compact[/fixref]',
        'test_create_tuple_idstyle_compact[/P4:6-multi1]',
        'test_create_tuple_idstyle_compact[/fixref_target_is_parametrized-0]',
        'test_create_tuple_idstyle_compact[/single_parametrized_lazy-foo]',
        # none should be equivalent to a plain old parametrize.
        'test_create_tuple_idstyle_none[single]',
        'test_create_tuple_idstyle_none[fixref]',
        'test_create_tuple_idstyle_none[multi1]',
        'test_create_tuple_idstyle_none[fixref_target_is_parametrized-0]',
        'test_create_tuple_idstyle_none[single_parametrized_lazy-foo]',
        # a callable passed to idstyle will receive ParamAlternative instances, here we use str(o)
        'test_create_tuple_idstyle_mygen[M(inputs,request_data)/P0/single]',
        'test_create_tuple_idstyle_mygen[M(inputs,request_data)/P1F/fixref]',
        'test_create_tuple_idstyle_mygen[M(inputs,request_data)/P4:6/-multi1]',
        'test_create_tuple_idstyle_mygen[M(inputs,request_data)/P6F/fixref_target_is_parametrized-0]',
        'test_create_tuple_idstyle_mygen[M(inputs,request_data)/P7F/single_parametrized_lazy-foo]',
        # an explicit list of ids work
        'test_create_tuple_ids_list[0]',
        'test_create_tuple_ids_list[1]',
        'test_create_tuple_ids_list[4]',
        'test_create_tuple_ids_list[6-0]',
        'test_create_tuple_ids_list[7-foo]',
        # when an explicit list of ids is passed at the same time than an idstyle the style is applied
        'test_create_tuple_ids_list_style[/0]',
        'test_create_tuple_ids_list_style[/1]',
        'test_create_tuple_ids_list_style[/P4:6-4]',
        'test_create_tuple_ids_list_style[/6-0]',
        'test_create_tuple_ids_list_style[/7-foo]',
        # a callable passed to ids will receive the argvalues
        'test_create_tuple_ids_mygen[Msingle]',
        'test_create_tuple_ids_mygen[Mfixref]',
        'test_create_tuple_ids_mygen[Mmulti1]',
        'test_create_tuple_ids_mygen[Mfixref_target_is_parametrized-0]',
        'test_create_tuple_ids_mygen[Msingle_parametrized_lazy-foo]',
        # when an explicit list of ids is passed at the same time than an idstyle the style is applied
        'test_create_tuple_ids_mygen_style[/Msingle]',
        'test_create_tuple_ids_mygen_style[/Mfixref]',
        'test_create_tuple_ids_mygen_style[/P4:6-Mmulti1]',
        'test_create_tuple_ids_mygen_style[/Mfixref_target_is_parametrized-0]',
        'test_create_tuple_ids_mygen_style[/Msingle_parametrized_lazy-foo]'
    ]

    single_res = [s.replace("tuple", "single").replace("(inputs,request_data)", "inputs_request_data") for s in tuple_res]

    assert list(module_results_dct) == tuple_res + single_res
