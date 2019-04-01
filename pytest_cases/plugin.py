from functools import partial

import pytest
from _pytest.python import CallSpec2

from pytest_cases.main_fixtures import UnionFixtureConfig
from _pytest.fixtures import scope2index

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature


# def pytest_sessionstart(session): fixture manager does not yet exist
#
#
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
#
#
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
# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_generate_tests(metafunc):
#     """
#     Unfortunately there is no hook between pytest_collectstart (where the fixtures have not yet been collected)
#     and pytest_generate_tests (that is called once per test function). So we use this hook only once, to get a chance
#     to replace some fixture definitions in the fixture manager.
#
#     :param metafunc:
#     :return:
#     """
#     try:
#         fxdefs = pytest_generate_tests.fm._arg2fixturedefs
#         fm = pytest_generate_tests.fm
#         del pytest_generate_tests.fm
#     except AttributeError:
#         pass
#     else:
#         for defname in fxdefs:
#             fixturedefs = fxdefs[defname]
#             for fd_idx in range(len(fixturedefs)):
#                 fixturedef = fixturedefs[fd_idx]
#                 # if hasattr(fixturedef.func, UNION_ATTR):
#                 #     fixturedefs[fd_idx] = finalize_union_fixture(fm, fixturedef)
#
#     # continue as usual
#     _ = yield


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_generate_tests(metafunc):
    """
    We use this hook to replace the 'partial' function of `metafunc` with our own below, before it is called by pytest

    :param metafunc:
    :return:
    """
    # override the parametrize method.
    # Note we could do it in a static way in pytest_sessionstart or plugin init hook, but we would need to save the

    metafunc.parametrize = partial(parametrize, metafunc)

    # now let pytest parametrize the call as usual
    _ = yield


def parametrize(metafunc, argnames, argvalues, indirect=False, ids=None, scope=None, **kwargs):
    """
    This alternate implementation of metafunc.parametrize creates a list of calls that is not just the cartesian
    product of all parameters (like the pytest behaviour).

    Instead, it offers an alternate list of calls takinginto account all union fixtures.

    For this, it replaces the `metafunc._calls` attribute with a `UnionCalls` instance, and feeds it with all parameters
    and parametrized fixtures independently (not doing any cross-product).

    The resulting `UnionCalls` instance is then able to dynamically behave like the correct list of calls, lazy-creating
    that list when it is used.
    """
    # create or grab our special container object
    if not isinstance(metafunc._calls, UnionCalls):
        if len(metafunc._calls) > 0:
            raise ValueError("This should not happen - please file an issue")
        # create a new one
        union_calls = UnionCalls(metafunc)
    else:
        # already exists - grab it
        union_calls = metafunc._calls

    # detect union fixtures
    if len(argvalues) == 1 and isinstance(argvalues[0], UnionFixtureConfig):
        if ',' in argnames or not isinstance(argnames, str):
            raise ValueError("Union fixtures can not be parametrized")
        union_fixture_name = argnames
        union_fixture_cfg = argvalues[0]
        if indirect is False or ids is not None or len(kwargs) > 0:
            raise ValueError("indirect or ids cannot be set on a union fixture")

        # add the union
        union_calls.add_union(union_fixture_name, union_fixture_cfg, scope=scope, **kwargs)
    else:
        # parametrize all unions
        union_calls.parametrize(argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)

    # # artificially forget about previous parametrization, so as to have a list of calls "just for this axis"
    # metafunc._calls = []
    # metafunc.__class__.parametrize(metafunc, argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)
    # # now add these calls to our object
    # union_calls.add_calls(metafunc._calls)

    # put our object back in place
    metafunc._calls = union_calls


NOT_USED = object()


class Node:
    __slots__ = ('parent', )

    def __init__(self, parent):
        self.parent = parent

    def parametrize(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        raise NotImplementedError()

    def to_list(self):
        raise NotImplementedError()


class SplitNode(Node):
    __slots__ = ('children_nodes', )

    def __init__(self, children_nodes, parent=None):
        Node.__init__(self, parent=parent)
        self.children_nodes = children_nodes

    def to_list(self):
        return [c for child in self.children_nodes for c in child.to_list()]

    def add_union(self, metafunc, union_fixture_name, cfg):
        for i in range(len(self.children_nodes)):
            c = self.children_nodes[i]
            if isinstance(c, SplitNode):
                # propagate
                c.add_union(metafunc, union_fixture_name, cfg)
            elif isinstance(c, LeafNode):
                # replace this child with a split
                self.children_nodes[i] = SplitNode.create(metafunc, union_fixture_name, replaced_node=c, cfg=cfg,
                                                          parent=self)
            else:
                raise TypeError("Unsupported Node type: %s" % type(c))

    def parametrize(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Parametrizes each of the partitions independently
        :return:
        """
        for child in self.children_nodes:
            child.parametrize(metafunc, force, argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)

    @staticmethod
    def create(metafunc,
               union_fixture_name,  # type: str
               cfg,                 # type: UnionFixtureConfig
               replaced_node=None,  # type: LeafNode
               parent=None          # type: Node
               ):
        """

        :param metafunc:
        :param union_fixture_name:
        :param cfg:
        :param replaced_node:
        :param parent:
        :return:
        """
        split_node = SplitNode([], parent=parent)
        split_node.children_nodes = []
        for i, sub_fix in enumerate(cfg.fixtures):
            new_node = FilteredLeafNode(metafunc, union_fixture_name, sub_fix,
                                        cfg.fixtures[0:i] + cfg.fixtures[(i + 1):], replaced_node, parent=split_node)
            split_node.children_nodes.append(new_node)

        return split_node


class LeafNode(Node):
    __slots__ = ('calls', )

    def __init__(self, calls, parent=None):
        Node.__init__(self, parent=parent)
        self.calls = calls

    def to_list(self):
        return self.calls

    @staticmethod
    def create_from(metafunc, argnames, argvalues, indirect, ids, scope, **kwargs):
        new = LeafNode([])
        new.parametrize(metafunc, True, argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)
        return new

    def should_be_discarded(self, argname):
        return False

    def parametrize(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Do the cartesian product of the parameters with what we already have.

        If force is set to True, parametrization will always happen. Otherwise, it will happen only if the argname is
        allowed.
        :return:
        """
        if force or not self.should_be_discarded(argnames):
            metafunc._calls = self.calls
            metafunc.__class__.parametrize(metafunc, argnames, argvalues, indirect=indirect, ids=ids, scope=scope,
                                           **kwargs)
            self.calls = metafunc._calls


class FilteredLeafNode(LeafNode):
    __slots__ = ('discarded_fixture_names', 'metafunc')

    def __init__(self,
                 metafunc,            #
                 union_fixture_name,  # type: str
                 fixture_name,        # type: str
                 discarded_fixture_names,  # type: List[str]
                 replaced_node,       # type: LeafNode
                 parent=None):

        # create the node with existing calls
        LeafNode.__init__(self, replaced_node.calls if replaced_node is not None else [], parent=parent)

        self.metafunc = metafunc

        # save the fixture names that are discarded
        if isinstance(replaced_node, FilteredLeafNode):
            discarded_fixture_names = replaced_node.discarded_fixture_names + discarded_fixture_names
        self.discarded_fixture_names = discarded_fixture_names

        # parametrize with the union node
        self.parametrize(metafunc, False, union_fixture_name, [fixture_name], indirect=True,
                         ids=['%s=%s' % (union_fixture_name, fixture_name)], scope=None)

    def to_list(self):
        # last minute parametrization: we have to make sure the union calls is set back in palce after that.
        bak_calls = self.metafunc._calls
        for missing in self.discarded_fixture_names:
            if missing not in self.calls[0].params:
                # parametrize with value None
                self.parametrize(self.metafunc, True, missing, [None], indirect=True,
                                 ids=['_'], scope=None)
                # remove the dummy id
                for callspec in self.metafunc._calls:
                    callspec._idlist.pop(-1)

        self.metafunc._calls = bak_calls

        return self.calls

    def should_be_discarded(self, argname):
        return argname in self.discarded_fixture_names


class UnionCalls:
    """
    This object replaces the list of calls that was in `metafunc._calls`.
    It behaves like a list, but it actually builds that list dynamically based on all parametrizations collected
    from the custom `metafunc.parametrize` above. When it is built once it is then stored in a cache
    """
    __slots__ = 'metafunc', 'names_required', 'tree', '_inner'

    def __init__(self, metafunc):
        self.metafunc = metafunc
        self.names_required = list(signature(metafunc.function).parameters)
        self._inner = None
        self.tree = None

    def add_union(self, union_fixture_name, union_fixture_cfg, scope=None, **kwargs):
        """

        :return:
        """
        if self.tree is None:
            # root node will be a split node
            self.tree = SplitNode.create(self.metafunc, union_fixture_name, cfg=union_fixture_cfg)
        elif isinstance(self.tree, LeafNode):
            # replace the whole tree
            self.tree = SplitNode.create(self.metafunc, union_fixture_name, replaced_node=self.tree,
                                         cfg=union_fixture_cfg)
        elif isinstance(self.tree, SplitNode):
            self.tree.add_union(self.metafunc, union_fixture_name, cfg=union_fixture_cfg)
        else:
            raise TypeError("This should not happen")

    def parametrize(self, argnames, argvalues, indirect=False, ids=None, scope=None, **kwargs):
        """

        """
        if self.tree is None:
            # root node will be a leaf node
            self.tree = LeafNode.create_from(self.metafunc, argnames, argvalues, indirect=indirect, ids=ids,
                                             scope=scope, **kwargs)
        else:
            # this is a fixture that is required by the function, force the parametrization.
            # otherwise, parametrize only the places where it is not already set
            force = argnames in self.names_required

            self.tree.parametrize(self.metafunc, force, argnames, argvalues, indirect=indirect, ids=ids, scope=scope,
                                  **kwargs)


    @property
    def calls_list(self):
        """
        Returns the list of calls. This field is lazily created on first access, based on `self.parametrizations`
        :return:
        """
        if self._inner is None:
            # create the definitive list
            self._inner = self.tree.to_list()

            # forget about all parametrizations now - this wont happen again
            self.tree = None

        return self._inner

    def __iter__(self):
        return iter(self.calls_list)

    def __getitem__(self, item):
        return self.calls_list[item]


def create_callspecs_list(metafunc, parametrizations):
    """
    Creates the list of CallSpec for metafunc, based on independent lists in `parametrizations`.

    :param metafunc:
    :param parametrizations:
    :return:
    """


    # at this stage, self.parametrizations is a list of the same lenght than the number of fixtures
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
    for i in range(len(parametrizations)):
        param_list = parametrizations[i]
        is_union = False
        if len(param_list) == 1:  # if there is only one value in this parameter ...
            if hasattr(param_list[0], 'params'):
                if len(param_list[0].params) == 1:  # and that value has a single param name
                    p, v = next(iter(param_list[0].params.items()))
                    if isinstance(v, UnionFixtureConfig):  # and the param value is the dummy mark
                        union_fixtures[p] = v
                        # del self.param_lists[i]
                        is_union = True
        if not is_union:
            n_fix_name = list(param_list[0].params.keys())
            if len(n_fix_name) != 1:
                raise ValueError("Unsupported internal error....")
            normal_fixtures[n_fix_name[0]] = param_list

    # (2) for each partition, do the multiplexing
    names_required = list(signature(metafunc.function).parameters)

    def add_slicers(_calls, union_fixture_name, selected_sub_fixture, param_index, scope):
        newcalls = []
        for callspec in _calls or [CallSpec2(metafunc)]:
            if union_fixture_name in callspec.params:
                raise ValueError("this should not happen: union fixture should be unique")

            # add the parameter to this callspec
            newcallspec = callspec.copy(metafunc)
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
            for callspec in all_the_calls or [CallSpec2(metafunc)]:
                # only do the product if the name is not already there
                if name not in callspec.params:
                    for _callspec_to_add in normal_fixtures[name]:
                        newcallspec = callspec.copy(metafunc)
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
            newcallspec = callspec.copy(metafunc)
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
