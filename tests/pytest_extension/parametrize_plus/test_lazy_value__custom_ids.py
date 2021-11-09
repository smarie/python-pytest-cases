# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>

# These tests are identical to the ones in test_lazy_value but there are custom ids
import pytest

from pytest_cases import parametrize, lazy_value


has_pytest_param = hasattr(pytest, 'param')


def id_generator(**objs):
    # return "-".join("%s=%s" % (k, v) for k, v in objs.items())
    # to get deterministic results we need this:
    if len(objs) > 1:
        assert set(objs.keys()) == {'a', 'b'}
        return "-".join("%s=%s" % (k, objs[k]) for k in ('a', 'b'))
    else:
        return "-".join("%s=%s" % (k, v) for k, v in objs.items())


def valtuple():
    return 1, 2


@pytest.mark.skipif(not has_pytest_param, reason="well")
def val_skipped_on_old_pytest():
    return "what"


def val():
    return 1


if not has_pytest_param:
    @parametrize("a", [lazy_value(val),
                       lazy_value(val_skipped_on_old_pytest),
                       lazy_value(val, id='A')], idgen=id_generator)
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a == 1


    @parametrize("a,b", [lazy_value(valtuple),
                         (1, lazy_value(val))], idgen=id_generator)
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        assert (a, b) == (1, 2) or (a, b) == (1, 1)


    def test_synthesis(module_results_dct):
        assert list(module_results_dct) == ['test_foo_single[a=val]',
                                            'test_foo_single[a=A]',
                                            'test_foo_multi[a=valtuple[0]-b=valtuple[1]]',  # normal: lazy_value is used for the whole tuple
                                                                      # AND we cannot use pytest.param in this version
                                                                      # AND there are no fixtures so we pass to normal @parametrize
                                            'test_foo_multi[a=1-b=val]']

else:
    @parametrize("a", [lazy_value(val),
                       pytest.param(lazy_value(val_skipped_on_old_pytest), marks=pytest.mark.skip),
                       pytest.param(lazy_value(val), id='B'),
                       pytest.param(lazy_value(val, id='ignored'), id='C'),
                       lazy_value(val, id='A')], idgen=id_generator)
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a == 1

    flag = False

    def valtuple_only_right_when_lazy():
        global flag
        if flag:
            return 0, -1
        else:
            raise ValueError("not yet ready ! you should call me later ")

    def valtuple_toskip():
        return 15, 2


    @parametrize("a,b", [lazy_value(valtuple),
                         lazy_value(valtuple, id="hello"),
                         lazy_value(valtuple_toskip, marks=pytest.mark.skip),
                         (1, lazy_value(valtuple_toskip, marks=pytest.mark.skip)),
                         pytest.param(lazy_value(valtuple_only_right_when_lazy), id='A'),
                         pytest.param(lazy_value(valtuple_toskip, marks=(pytest.mark.xfail,)), id='Wrong', marks=pytest.mark.skip),
                         (1, lazy_value(val)),
                         pytest.param(1, lazy_value(val), id='B')], idgen=id_generator)
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        global flag
        flag = True
        assert (a, b) in [(1, 2), (1, 1), (0, -1)]


    def test_synthesis2(module_results_dct):
        assert list(module_results_dct) == ['test_foo_single[a=val]',
                                            'test_foo_single[B]',
                                            'test_foo_single[C]',
                                            'test_foo_single[a=A]',
                                            'test_foo_multi[a=valtuple[0]-b=valtuple[1]]',
                                            'test_foo_multi[a=hello[0]-b=hello[1]]',
                                            'test_foo_multi[A]',
                                            'test_foo_multi[a=1-b=val]',
                                            'test_foo_multi[B]']
