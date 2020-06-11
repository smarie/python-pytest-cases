import pytest

from pytest_cases import parametrize_plus, lazy_value, fixture_plus, fixture_ref


def valtuple():
    return 1, 2


def val():
    return 1


@fixture_plus
@parametrize_plus("i", [lazy_value(val), 11])
def tfix(i):
    return i, i+2


@fixture_plus
@parametrize_plus("i", [5, lazy_value(val)])
def vfix(i):
    return -i


flag = False


def valtuple_toskip():
    return 15, 2


def valtuple_only_right_when_lazy():
    global flag
    if flag:
        return 0, -1
    else:
        raise ValueError("not yet ready ! you should call me later ")


has_pytest_param = hasattr(pytest, 'param')
if not has_pytest_param:
    @parametrize_plus("a,b", [lazy_value(valtuple),
                              lazy_value(valtuple, id='A'),
                              fixture_ref(tfix),
                              (fixture_ref(vfix), lazy_value(val)),
                              (lazy_value(val, id='B'), fixture_ref(vfix)),
                              (fixture_ref(vfix), fixture_ref(vfix)),
                              ], debug=True)
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        global flag
        flag = True
        assert (a, b) in ((1, 2), (1, 1), (1, 3), (-5, 1), (11, 13), (-1, 1), (1, -5), (1, -1), (-5, -5), (-1, -1))


    def test_synthesis2(module_results_dct):
        assert list(module_results_dct) == ['test_foo_multi[a_b_is_P0toP1-valtuple]',
                                            'test_foo_multi[a_b_is_P0toP1-A]',
                                            'test_foo_multi[a_b_is_tfix-val]',
                                            'test_foo_multi[a_b_is_tfix-11]',
                                            'test_foo_multi[a_b_is_P3-5]',
                                            'test_foo_multi[a_b_is_P3-val]',
                                            'test_foo_multi[a_b_is_P4-5]',
                                            'test_foo_multi[a_b_is_P4-val]',
                                            'test_foo_multi[a_b_is_P5-5]',
                                            'test_foo_multi[a_b_is_P5-val]'
                                            ]

else:
    @parametrize_plus("a,b", [lazy_value(valtuple),
                              pytest.param(lazy_value(valtuple, id='A')),
                              pytest.param(lazy_value(valtuple_toskip), id='Wrong', marks=pytest.mark.skip),
                              fixture_ref(tfix),
                              (fixture_ref(vfix), lazy_value(val)),
                              pytest.param(lazy_value(val), fixture_ref(vfix), id='B'),
                              (fixture_ref(vfix), fixture_ref(vfix)),
                              ], debug=True)
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        global flag
        flag = True
        assert (a, b) in ((1, 2), (1, 1), (1, 3), (-5, 1), (11, 13), (-1, 1), (1, -5), (1, -1), (-5, -5), (-1, -1))


    def test_synthesis2(module_results_dct):
        assert list(module_results_dct) == ['test_foo_multi[a_b_is_P0toP2-valtuple]',
                                            'test_foo_multi[a_b_is_P0toP2-A]',
                                            'test_foo_multi[a_b_is_tfix-val]',
                                            'test_foo_multi[a_b_is_tfix-11]',
                                            'test_foo_multi[a_b_is_P4-5]',
                                            'test_foo_multi[a_b_is_P4-val]',
                                            'test_foo_multi[B-5]',
                                            'test_foo_multi[B-val]',
                                            'test_foo_multi[a_b_is_P6-5]',
                                            'test_foo_multi[a_b_is_P6-val]'
                                            ]
