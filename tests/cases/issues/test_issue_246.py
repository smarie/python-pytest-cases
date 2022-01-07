#  Authors: Sylvain MARIE <sylvain.marie@se.com>
#            + All contributors to <https://github.com/smarie/python-pyfields>
#
#  License: 3-clause BSD, <https://github.com/smarie/python-pyfields/blob/master/LICENSE>
from distutils.version import LooseVersion

import pytest
from pytest_cases import parametrize_with_cases

PYTEST_VERSION = LooseVersion(pytest.__version__)
PYTEST3_OR_GREATER = PYTEST_VERSION >= LooseVersion('3.0.0')

if PYTEST3_OR_GREATER:
    @pytest.mark.foo
    class MarkedCases:
        @pytest.mark.bar
        def case_instance(self):
            return 1

        @staticmethod
        @pytest.mark.bar
        def case_static():
            return 2

        @classmethod
        @pytest.mark.bar
        def case_classmethod(cls):
            return 3


    @pytest.mark.foo
    class TestNominal:
        @pytest.mark.bar
        def test_pytest_nominal(self, request):
            # make sure the mark has been propagated from class to test
            all_marks = tuple(m.name for m in request.node.iter_markers())
            assert set(all_marks) == {'bar', 'foo'}


    @parametrize_with_cases('a', cases=MarkedCases)
    def test_pytest_cases(a, request):
        # make sure the mark has been propagated from case class to test
        all_marks = tuple(m.name for m in request.node.iter_markers())
        assert set(all_marks) == {'parametrize', 'foo', 'bar'}


    @parametrize_with_cases('b', cases=MarkedCases)
    def test_pytest_cases2(b, request):
        # make sure the mark has been propagated from case class to test, but not a second time
        all_marks = tuple(m.name for m in request.node.iter_markers())
        assert set(all_marks) == {'parametrize', 'foo', 'bar'}
