from functools import partial

import pytest
from _pytest.python import CallSpec2

from pytest_cases.main_fixtures import UnionAttrParam
from _pytest.fixtures import scope2index

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature


# def pytest_sessionstart(session): fixture manager does not yet exist


# @pytest.hookimpl(tryfirst=True)
# def pytest_collectstart(collector):
#     # save the fixture manager for later use in pytest_generate_tests
#     fm = collector.session._fixturemanager
#     wrapper = FMWrapper(fm)
#     # fm.getfixtureinfo = partial(getfixtureinfo, fm)
#     # fm.getfixtureclosure = partial(getfixtureclosure, fm)
#     fm.pytest_generate_tests = wrapper.pytest_generate_tests
#
#
# class FMWrapper(ObjectProxy):
#     def pytest_generate_tests(self, metafunc):
#         return self.__wrapped__.pytest_generate_tests(metafunc)


# class MyFixtureInfo:
#     def __init__(self, fi):
#         self.fi = fi
#
#     def __getattr__(self, item):
#         return getattr(self.fi, item)
#
#
# def getfixtureinfo(self, node, func, cls, funcargs=True, *args, **kwargs):
#     fixture_info = self.__class__.getfixtureinfo(self, node, func, cls, funcargs=funcargs, *args, **kwargs)
#     return MyFixtureInfo(fixture_info)
#
#
# def getfixtureclosure(self, fixturenames, parentnode, *args, **kwargs):
#     parentid = parentnode.nodeid
#     return self.__class__.getfixtureclosure(self, fixturenames, parentnode, *args, **kwargs)
#
#
@pytest.hookimpl(tryfirst=True, hookwrapper=True) #tryfirst=True, hookwrapper=True)
def pytest_generate_tests(metafunc):
    """
    Unfortunately there is no hook between pytest_collectstart (where the fixtures have not yet been collected)
    and pytest_generate_tests (that is called once per test function). So we use this hook only once, to get a chance
    to replace some fixture definitions.

    :param metafunc:
    :return:
    """
    # try:
    #     fxdefs = pytest_generate_tests.fm._arg2fixturedefs
    #     fm = pytest_generate_tests.fm
    #     del pytest_generate_tests.fm
    # except AttributeError:
    #     pass
    # else:
    #     for defname in fxdefs:
    #         fixturedefs = fxdefs[defname]
    #         for fd_idx in range(len(fixturedefs)):
    #             fixturedef = fixturedefs[fd_idx]
    #             # if hasattr(fixturedef.func, UNION_ATTR):
    #             #     fixturedefs[fd_idx] = finalize_union_fixture(fm, fixturedef)

    # now let's add the union fixture.
    metafunc.parametrize = partial(parametrize, metafunc)

    # now let pytest parametrize the call as usual
    _ = yield


NOT_USED = object()


class UnionCalls:

    def __init__(self, metafunc):
        self.metafunc = metafunc
        self.param_lists = []

    @property
    def inner(self):
        # here we have to construct the list of callspec

        # at this stage, self.new is a list of the same lenght than the number of fixtures
        # required (directly or indirectly) by this function.

        # what happens usually in metafunc.parametrize is multiplexing:
        # newcallspec = callspec.copy(self)
        # newcallspec.setmulti2(valtypes, argnames, param.values, a_id,
        #                       param.marks, scopenum, param_index)
        # newcalls.append(newcallspec)

        # what we want to do is
        # (1) construct a partition of fixtures
        union_fixtures = dict()
        normal_fixtures = dict()
        # param_lists = copy(self.param_lists)  # create a copy because we'll be deleting some in the middle
        for i in range(len(self.param_lists)):
            param_list = self.param_lists[i]
            is_union = False
            if len(param_list) == 1:  # if there is only one value in this parameter ...
                if hasattr(param_list[0], 'params'):
                    if len(param_list[0].params) == 1:  # and that value has a single param name
                        p, v = next(iter(param_list[0].params.items()))
                        if isinstance(v, UnionAttrParam):  # and the param value is the dummy mark
                            union_fixtures[p] = v
                            # del self.param_lists[i]
                            is_union = True
            if not is_union:
                n_fix_name = list(param_list[0].params.keys())
                if len(n_fix_name) != 1:
                    raise ValueError("Unsupported internal error....")
                normal_fixtures[n_fix_name[0]] = param_list

        # (2) for each partition, do the multiplexing
        names_required = list(signature(self.metafunc.function).parameters)

        def add_slicers(_calls, union_fixture_name, selected_sub_fixture, param_index, scope):
            newcalls = []
            for callspec in _calls or [CallSpec2(self.metafunc)]:
                if union_fixture_name in callspec.params:
                    raise ValueError("this should not happen: union fixture should be unique")

                #add the parameter to this callspec
                newcallspec = callspec.copy(self.metafunc)
                scopenum = scope2index(scope, descr='call to {0}'.format('hack'))
                newcallspec.setmulti2({union_fixture_name: "params"}, [union_fixture_name], [selected_sub_fixture],
                                      'dummy', [], scopenum, param_index)
                # remove the dummy id
                newcallspec._idlist.pop(-1)
                callspec.params[union_fixture_name] = selected_sub_fixture
                newcalls.append(newcallspec)

            return newcalls

        def get_calls(all_the_calls, name):
            if name in union_fixtures:
                separate_calls = []
                for i, sub_fixture in enumerate(union_fixtures[name].fixtures):
                    # take the calls that we have listed so far,
                    scope = 'function'  # TODO understand what to do
                    _calls_with_slicer = add_slicers(all_the_calls, name, sub_fixture, i, scope)

                    # add all the others as dummy values if they are not there already
                    # all_unused_fixtures = set(union_fixtures[name].fixtures) - {sub_fixture}
                    # _calls_with_slicer2 = []
                    # for callspec in _calls_with_slicer:
                    #     missing_names = all_unused_fixtures - set(callspec.params)
                    #     already_there_names = set(callspec.params).intersection(all_unused_fixtures)
                    #     if len(already_there_names) > 0:
                    #         # TODO what if they are there already ?
                    #         raise ValueError("We dont know yet what to do")
                    #     newcallspec = callspec.copy(self.metafunc)
                    #     vartypes = {argname: 'params' for argname in missing_names}
                    #     paramvalues = [NOT_USED for argname in missing_names]
                    #     scope = 'function'  # TODO understand what to do
                    #     scopenum = scope2index(scope, descr='call to {0}'.format('hack'))
                    #     param_index = -1
                    #     newcallspec.setmulti2(vartypes, missing_names, paramvalues, 'dummy',
                    #                           (), scopenum, param_index)
                    #     # remove the dummy id
                    #     newcallspec._idlist.pop(-1)
                    #     _calls_with_slicer2.append(newcallspec)
                    #
                    # separate_calls += get_calls(_calls_with_slicer2, sub_fixture)
                    separate_calls += get_calls(_calls_with_slicer, sub_fixture)
                return separate_calls
            else:
                # normal fixture. do an intelligent product (= only for callspecs that do not have this fixture)
                newcalls = []
                for callspec in all_the_calls or [CallSpec2(self.metafunc)]:
                    # only do the product if the name is not already there
                    if name not in callspec.params:
                        for _callspec_to_add in normal_fixtures[name]:
                            newcallspec = callspec.copy(self.metafunc)
                            if len(_callspec_to_add._idlist) != 1:
                                raise ValueError("each such callspec is supposed to represent a single fixture")
                            # there is a single id, a single arg, a single param
                            a_id = _callspec_to_add._idlist[0]
                            argname, paramvalue = next(iter(_callspec_to_add.params.items()))
                            scopenum = _callspec_to_add._arg2scopenum[argname]
                            param_index = _callspec_to_add.indices[argname]
                            newcallspec.setmulti2({argname: "params"}, [argname], [paramvalue], a_id,
                                                  _callspec_to_add.marks, scopenum, param_index)

                            newcalls.append(newcallspec)
                    else:
                        newcalls.append(callspec)
                return newcalls

        # trigger building the list
        all_the_calls = []
        for name in names_required:
            all_the_calls = get_calls(all_the_calls, name)

        # finally add missing param values in each callspec
        risky_names = {name for union_fix_defs in union_fixtures.values() for name in union_fix_defs.fixtures}
        if len(risky_names) == 0:
            return all_the_calls
        else:
            final_calls = []
            for callspec in all_the_calls:
                missing_names = set(risky_names) - set(callspec.params)
                newcallspec = callspec.copy(self.metafunc)
                vartypes = {argname: 'params' for argname in missing_names}
                paramvalues = [None for argname in missing_names]
                scope = 'function'  # TODO understand what to do
                scopenum = scope2index(scope, descr='call to {0}'.format('hack'))
                param_index = -1
                newcallspec.setmulti2(vartypes, missing_names, paramvalues, 'dummy',
                                      (), scopenum, param_index)
                # remove the dummy id
                newcallspec._idlist.pop(-1)
                final_calls.append(newcallspec)

            return final_calls

    def __iter__(self):
        return iter(self.inner)

    def __getitem__(self, item):
        return self.inner[item]

    def add_calls(self, added):
        self.param_lists.append(added)


def parametrize(metafunc, argnames, argvalues, indirect=False, ids=None, scope=None, **kwargs):

    # save the existing calls
    before_calls = metafunc._calls
    if not isinstance(before_calls, UnionCalls):
        before_calls = UnionCalls(metafunc)

    # parametrize "dummy" for just this parameter set
    metafunc._calls = []
    metafunc.__class__.parametrize(metafunc, argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)

    # put back the calls
    before_calls.add_calls(metafunc._calls)
    metafunc._calls = before_calls


# def finalize_union_fixture(fm, fixturedef):
#     """
#
#     :param fxdefs:
#     :return:
#     """
#     # (1) grab all fixtures it depends upon
#     depends_fixtures = getattr(fixturedef.func, UNION_ATTR)
#     f_defs = []
#     for f in depends_fixtures:
#         if not isinstance(f, str):
#             f = f.func_name
#
#         # a fixture name - use the fixture manager
#         all_defs = request.session._fixturemanager.getfixturedefs(f, request.node.nodeid)
#         if len(all_defs) != 1:
#             raise ValueError("Fixture name used in `fixture_union` does not seem to be known: %s" % f)
#         f_defs.append(all_defs[0])
#
#     # get a reference list of scopes ordered from 0: session to n: function
#     f_scope_idx = scopes.index("function")
#     if f_scope_idx == 0:
#         scopes_ = reversed(scopes)
#     elif f_scope_idx == len(scopes) - 1:
#         scopes_ = scopes
#     else:
#         raise ValueError("Internal error - pytest seems to have changed its internal scopes definition")
#
#     # (2) find the smallest scope and create a union of the parameters lists
#     final_scope_idx = 0
#     fix_and_param = []
#     for f_def in f_defs:
#         f_scope_idx = scopes.index(f_def.scope)
#         if f_scope_idx > final_scope_idx:
#             final_scope_idx = f_scope_idx
#
#         if f_def.params is None:
#             fix_and_param.append((f_def.func, None))
#         else:
#             fix_and_param += [(f_def.func, p) for p in f_def.params]
#
#     # (3) finally create the function
#     fixturedef.scope = scopes[final_scope_idx]
#     fixturedef.params = fix_and_param
#     def _union_fixture_impl(request):
#         return request.param
#     fixturedef.func = _union_fixture_impl
#     fixturedef.argnames = ['request']
#
#     return fixturedef
