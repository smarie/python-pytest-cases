from collections import OrderedDict
from functools import partial

import pytest
# from _pytest.python import CallSpec2

from pytest_cases.main_fixtures import UnionFixtureConfig
# from _pytest.fixtures import scope2index

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

    For this, it replaces the `metafunc._calls` attribute with a `CallsReactor` instance, and feeds it with all parameters
    and parametrized fixtures independently (not doing any cross-product).

    The resulting `CallsReactor` instance is then able to dynamically behave like the correct list of calls, lazy-creating
    that list when it is used.
    """
    # create our special container object if needed
    if not isinstance(metafunc._calls, CallsReactor):
        if len(metafunc._calls) > 0:
            raise ValueError("This should not happen - please file an issue")
        metafunc._calls = CallsReactor(metafunc)

    # grab it
    calls_reactor = metafunc._calls

    # detect union fixtures
    if len(argvalues) == 1 and isinstance(argvalues[0], UnionFixtureConfig):
        if ',' in argnames or not isinstance(argnames, str):
            raise ValueError("Union fixtures can not be parametrized")
        union_fixture_name = argnames
        union_fixture_cfg = argvalues[0]
        if indirect is False or ids is not None or len(kwargs) > 0:
            raise ValueError("indirect or ids cannot be set on a union fixture")

        # add a union parametrization (but do not apply it)
        calls_reactor.add_union(union_fixture_name, union_fixture_cfg, scope=scope, **kwargs)
    else:
        # add a normal parametrization (but do not apply it)
        calls_reactor.add_param(argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)

    # put our object back in place - not needed anymore
    # metafunc._calls = calls_reactor


class Node:
    __slots__ = ('parent', )

    def __init__(self, parent):
        self.parent = parent

    def parametrize(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        raise NotImplementedError()

    def finalize_parametrization(self):
        raise NotImplementedError()

    def to_list(self):
        raise NotImplementedError()

    def all_ids(self):
        return [c.id for c in self.to_list()]


class SplitNode(Node):
    __slots__ = ('children_nodes', )

    def __init__(self, children_nodes, parent=None):
        Node.__init__(self, parent=parent)
        self.children_nodes = children_nodes

    def __repr__(self):
        return "|".join(["[%s]" % n for n in self.children_nodes])

    def finalize_parametrization(self):
        for child in self.children_nodes:
            child.finalize_parametrization()

    def to_list(self):
        return [c for child in self.children_nodes for c in child.to_list()]

    def add_union(self, metafunc, union_fixture_name, cfg, scope, **kwargs):
        """
        Returns a list of newly created leaves
        """
        created_nodes = []
        for i in range(len(self.children_nodes)):
            c = self.children_nodes[i]
            if isinstance(c, SplitNode):
                # propagate
                created_nodes += c.add_union(metafunc, union_fixture_name, cfg, scope, **kwargs)
            elif isinstance(c, LeafNode):
                # replace this child with a split node
                self.children_nodes[i] = SplitNode.create_for_leaf_replacement(metafunc, union_fixture_name, cfg=cfg,
                                                                               replaced_node=c, scope=scope, **kwargs)
                created_nodes += self.children_nodes[i].children_nodes
            else:
                raise TypeError("Unsupported Node type: %s" % type(c))

        return created_nodes

    def parametrize(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Parametrizes each of the partitions independently
        :return:
        """
        for child in self.children_nodes:
            child.parametrize(metafunc, force, argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)

    @staticmethod
    def create_for_leaf_replacement(metafunc,
                                    union_fixture_name,  # type: str
                                    cfg,  # type: UnionFixtureConfig
                                    scope,  # type: Optional[str]
                                    replaced_node=None,  # type: Optional[LeafNode]
                                    **kwargs
                                    ):
        """

        :param metafunc:
        :param union_fixture_name:
        :param cfg:
        :param replaced_node:
        :param parent:
        :return:
        """
        if replaced_node is not None:
            parent = replaced_node.parent
            if isinstance(replaced_node, LeafNode):
                # break down the list of calls in sublists of one element.
                init_calls_list = [[c] for c in replaced_node.calls]
            else:
                raise ValueError("this should not happen")

            if isinstance(replaced_node, FilteredLeafNode):
                i_sel = replaced_node._selections
                i_dis = replaced_node._discarded_fixture_names
            else:
                i_sel = None
                i_dis = None

        else:
            parent = None
            init_calls_list = [[]]
            i_sel = None
            i_dis = None

        # new node
        new_node = SplitNode([], parent=parent)
        for init_calls in init_calls_list:
            for i, sub_fix in enumerate(cfg.fixtures):
                new_leaf = FilteredLeafNode(metafunc, union_fixture_name, sub_fix,
                                            cfg.fixtures[0:i] + cfg.fixtures[(i + 1):], initial_calls=init_calls,
                                            initial_selections=i_sel, initial_discarded_names=i_dis,
                                            scope=scope, parent=new_node, **kwargs)
                new_node.children_nodes.append(new_leaf)

        return new_node


class LeafNode(Node):
    __slots__ = ('calls', )

    def __init__(self, calls, parent=None):
        Node.__init__(self, parent=parent)
        self.calls = calls

    def finalize_parametrization(self):
        pass

    def to_list(self):
        return self.calls

    @staticmethod
    def create_parametrized(metafunc, argnames, argvalues, indirect, ids, scope, **kwargs):
        new = LeafNode([])
        new.parametrize(metafunc, True, argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)
        return new

    def parametrize(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Do the cartesian product of the parameters with what we already have.

        'force' is a keyword for the subclass.
        :return:
        """
        bak = metafunc._calls
        metafunc._calls = self.calls
        metafunc.__class__.parametrize(metafunc, argnames, argvalues, indirect=indirect, ids=ids, scope=scope,
                                       **kwargs)
        self.calls = metafunc._calls
        metafunc._calls = bak

    def discard_last_id(self):
        """remove the last id in all callspecs"""
        for callspec in self.calls:
            callspec._idlist.pop(-1)


class FilteredLeafNode(LeafNode):
    __slots__ = ('metafunc', 'union_fixture_name', '_selections', '_discarded_fixture_names',)

    def __init__(self,
                 metafunc,  #
                 union_fixture_name,       # type: str
                 selected_fixture_name,    # type: str
                 discarded_fixture_names,  # type: List[str]
                 initial_calls=None,       # type: Optional[Node]
                 initial_selections=None,
                 initial_discarded_names=None,
                 parent=None,              # type: Optional[Node]
                 scope=None,
                 **kwargs):

        # create the node with existing calls
        LeafNode.__init__(self, initial_calls, parent=parent)

        self.metafunc = metafunc
        self.union_fixture_name = union_fixture_name

        # save the fixture names that are selected/discarded
        self._selections = [(union_fixture_name, selected_fixture_name)]
        self._discarded_fixture_names = discarded_fixture_names
        if initial_selections is not None:
            self._selections = initial_selections + self._selections
        if initial_discarded_names is not None:
            self._discarded_fixture_names = initial_discarded_names + self._discarded_fixture_names

        # parametrize with the union node
        # _id = '%s=%s' % (union_fixture_name, selected_fixture_name)
        _id = '%s' % selected_fixture_name
        self.parametrize(metafunc, False, union_fixture_name, [selected_fixture_name], indirect=True,
                         ids=[_id], scope=scope, **kwargs)

        # remove the dummy id
        # self.discard_last_id()

    @property
    def selections(self):
        selections = OrderedDict()
        parent = self.parent
        while parent is not None:
            if isinstance(parent, FilteredLeafNode):
                # we have to pile up with the ones from the parents
                selections.update(parent.selections)
                break
            parent = parent.parent

        for s in self._selections:
            selections[s[0]] = s[1]
        return selections

    @property
    def discarded_fixture_names(self):
        discarded_fixture_names = []
        parent = self.parent
        while parent is not None:
            if isinstance(parent, FilteredLeafNode):
                # we have to pile up with the ones from the parents
                discarded_fixture_names = parent.discarded_fixture_names
                break
            parent = parent.parent

        return discarded_fixture_names + self._discarded_fixture_names

    def __repr__(self):
        return '&'.join(['%s=%s' % (k, v) for k, v in self.selections.items()])

    @property
    def last_selected(self):
        return next(iter(reversed(self.selections.values())))

    def finalize_parametrization(self):
        """

        :return:
        """
        for missing in self.discarded_fixture_names:
            if missing not in self.calls[0].params:
                # parametrize with value None
                self.parametrize(self.metafunc, True, missing, [None], indirect=True,
                                 ids=['_'], scope=None)
                # remove the dummy id
                self.discard_last_id()

    def parametrize(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Same than

        If force is set to True, parametrization will always happen. Otherwise, it will happen only if the argname is
        allowed.
        :return:
        """
        if len(self.calls) > 0 and argnames in self.calls[0].params:
            # already set.
            return
        elif force or (argnames not in self.discarded_fixture_names):
            LeafNode.parametrize(self, metafunc, force, argnames, argvalues, indirect=indirect, ids=ids, scope=scope,
                                 **kwargs)


# class UnionLeafNode(Node):
#
#     __slots__ = ('children', )
#
#     def __init__(self, children, parent=None):
#         self.children = children
#         Node.__init__(parent=parent)
#
#     @staticmethod
#     def create(metafunc,
#                union_fixture_name,  # type: str
#                cfg,  # type: UnionFixtureConfig
#                scope,  # type: Optional[str]
#                replaced_node=None,  # type: Optional[LeafNode]
#                parent=None,  # type: Node
#                **kwargs
#                ):
#         children = []
#         new = UnionLeafNode(children)
#
#         for call in replaced_node.calls:
#             splt = SplitNode.create(metafunc, union_fixture_name, replaced_node=c, cfg=cfg,
#                                     parent=new, scope=scope, **kwargs)
#
#         return new


class CallsReactor:
    """
    This object replaces the list of calls that was in `metafunc._calls`.
    It behaves like a list, but it actually builds that list dynamically based on all parametrizations collected
    from the custom `metafunc.parametrize` above. When it is built once it is then stored in a cache
    """
    __slots__ = 'metafunc', '_pending', '_tree'

    def __init__(self, metafunc):
        self.metafunc = metafunc
        self._tree = None
        self._pending = []

    def add_union(self, union_fixture_name, union_fixture_cfg, scope=None, **kwargs):
        """ Adds a union to the pending operations """
        self._pending.append((SplitNode, union_fixture_name, union_fixture_cfg, scope, kwargs))

    def add_param(self, argnames, argvalues, indirect=False, ids=None, scope=None, **kwargs):
        """ Adds a parameter to the pending operations """
        self._pending.append((LeafNode, argnames, argvalues, indirect, ids, scope, kwargs))

    # -- list facade --

    def __iter__(self):
        return iter(self.calls_list)

    def __getitem__(self, item):
        return self.calls_list[item]

    @property
    def calls_list(self):
        """
        Returns the list of calls. This field is lazily created on first access, based on `self.parametrizations`
        :return:
        """
        if self._tree is None:
            # create the definitive tree.
            self.create_tree_from_pending_parametrizations()

        return self._tree.to_list()

    # ---

    def create_tree_from_pending_parametrizations(self):
        """
        Takes all parametrization operations that are pending in `self._pending`,
        and creates a parametrization tree out of them.

        self._pending is set to None afterwards
        :return:
        """
        bak_calls = self.metafunc._calls

        # parameterize the tree
        names_required = list(signature(self.metafunc.function).parameters)
        for i in range(len(self._pending)):
            self.advanced_parametrize(names_required, self._pending[i], self._pending[i+1:])
        self._tree.finalize_parametrization()

        self.metafunc._calls = bak_calls

        # forget about all parametrizations now - this wont happen again
        self._pending = None

    def advanced_parametrize(self, names_required, single_pmz, remaining_pmzs, node=None, force=None):
        """

        :param names_required:
        :param single_pmz:
        :param remaining_pmzs:
        :return:
        """
        work_node = self._tree if node is None else node

        print("parametrizing node %s (with current ids %s) with %s"
              "" % (work_node, work_node.all_ids() if work_node is not None else None, single_pmz))

        if single_pmz[0] is SplitNode:
            # (A) a 'union' fixture
            union_fixtr_name, union_fixtr_cfg, scope, kwargs = single_pmz[1:]
            if work_node is None or isinstance(work_node, LeafNode):
                # root node will be a split node
                if work_node is not None:
                    parent = work_node.parent
                    i = parent.children_nodes.index(work_node)
                else:
                    parent, i = None, None
                work_node = SplitNode.create_for_leaf_replacement(self.metafunc, union_fixtr_name,
                                                                  replaced_node=work_node, cfg=union_fixtr_cfg,
                                                                  scope=scope, **kwargs)
                if parent is not None:
                    parent.children_nodes[i] = work_node

                leaves = work_node.children_nodes
            elif isinstance(work_node, SplitNode):
                leaves = work_node.add_union(self.metafunc, union_fixtr_name, cfg=union_fixtr_cfg, scope=scope,
                                             **kwargs)
            else:
                raise TypeError("This should not happen")

            # for each newly created leaf, parametrize it with the fixture it is supposed to use
            force = force or (union_fixtr_name in names_required)
            for leaf in leaves:
                i = CallsReactor.find_pending_param_for_fixture_name(leaf.last_selected,
                                                                     remaining_pmzs)
                if i is not None:
                    self.advanced_parametrize(names_required, remaining_pmzs[i], remaining_pmzs[i+1:], node=leaf,
                                              force=force)
                else:
                    # that can happen when two unions rely on the same fixture.
                    pass

        else:
            # (B) a normal parameter fixture
            argnames, argvalues, indirect, ids, scope, kwargs = single_pmz[1:]
            if work_node is None:
                # root node will be a leaf node
                work_node = LeafNode.create_parametrized(self.metafunc, argnames, argvalues, indirect=indirect, ids=ids,
                                                         scope=scope, **kwargs)
            else:
                # this is a fixture that is required by the function, force the parametrization.
                # otherwise, parametrize only the places where it is not already set
                force = force or (argnames in names_required)
                work_node.parametrize(self.metafunc, force, argnames, argvalues, indirect=indirect, ids=ids,
                                      scope=scope, **kwargs)

        print("> node %s parametrized. Current ids %s" % (work_node, work_node.all_ids()))

        # set back the field if needed
        if node is None:
            self._tree = work_node

    @staticmethod
    def find_pending_param_for_fixture_name(f_name, remaining_pmzs):
        for i, p in enumerate(remaining_pmzs):
            if p[1] == f_name:
                return i


# NOT_USED = object()
#
#
# def create_callspecs_list(metafunc, parametrizations):
#     """
#     Creates the list of CallSpec for metafunc, based on independent lists in `parametrizations`.
#
#     :param metafunc:
#     :param parametrizations:
#     :return:
#     """
#
#
#     # at this stage, self.parametrizations is a list of the same lenght than the number of fixtures
#     # required (directly or indirectly) by this function.
#
#     # what happens usually in metafunc.parametrize is multiplexing:
#     # newcallspec = callspec.copy(self)
#     # newcallspec.setmulti2(valtypes, argnames, param.values, a_id,
#     #                       param.marks, scopenum, param_index)
#     # newcalls.append(newcallspec)
#
#     # what we want to do is
#     # (1) construct a partition of fixtures
#     union_fixtures = dict()
#     normal_fixtures = dict()
#     # param_lists = copy(self.param_lists)  # create a copy because we'll be deleting some in the middle
#     for i in range(len(parametrizations)):
#         param_list = parametrizations[i]
#         is_union = False
#         if len(param_list) == 1:  # if there is only one value in this parameter ...
#             if hasattr(param_list[0], 'params'):
#                 if len(param_list[0].params) == 1:  # and that value has a single param name
#                     p, v = next(iter(param_list[0].params.items()))
#                     if isinstance(v, UnionFixtureConfig):  # and the param value is the dummy mark
#                         union_fixtures[p] = v
#                         # del self.param_lists[i]
#                         is_union = True
#         if not is_union:
#             n_fix_name = list(param_list[0].params.keys())
#             if len(n_fix_name) != 1:
#                 raise ValueError("Unsupported internal error....")
#             normal_fixtures[n_fix_name[0]] = param_list
#
#     # (2) for each partition, do the multiplexing
#     names_required = list(signature(metafunc.function).parameters)
#
#     def add_slicers(_calls, union_fixture_name, selected_sub_fixture, param_index, scope):
#         newcalls = []
#         for callspec in _calls or [CallSpec2(metafunc)]:
#             if union_fixture_name in callspec.params:
#                 raise ValueError("this should not happen: union fixture should be unique")
#
#             # add the parameter to this callspec
#             newcallspec = callspec.copy(metafunc)
#             scopenum = scope2index(scope, descr='call to {0}'.format('hack'))
#             newcallspec.setmulti2({union_fixture_name: "params"}, [union_fixture_name], [selected_sub_fixture],
#                                   'dummy', [], scopenum, param_index)
#             # remove the dummy id
#             newcallspec._idlist.pop(-1)
#             callspec.params[union_fixture_name] = selected_sub_fixture
#             newcalls.append(newcallspec)
#
#         return newcalls
#
#     def get_calls(all_the_calls, name):
#         if name in union_fixtures:
#             separate_calls = []
#             for i, sub_fixture in enumerate(union_fixtures[name].fixtures):
#                 # take the calls that we have listed so far,
#                 scope = 'function'  # TODO understand what to do
#                 _calls_with_slicer = add_slicers(all_the_calls, name, sub_fixture, i, scope)
#
#                 # add all the others as dummy values if they are not there already
#                 # all_unused_fixtures = set(union_fixtures[name].fixtures) - {sub_fixture}
#                 # _calls_with_slicer2 = []
#                 # for callspec in _calls_with_slicer:
#                 #     missing_names = all_unused_fixtures - set(callspec.params)
#                 #     already_there_names = set(callspec.params).intersection(all_unused_fixtures)
#                 #     if len(already_there_names) > 0:
#                 #         # TODO what if they are there already ?
#                 #         raise ValueError("We dont know yet what to do")
#                 #     newcallspec = callspec.copy(self.metafunc)
#                 #     vartypes = {argname: 'params' for argname in missing_names}
#                 #     paramvalues = [NOT_USED for argname in missing_names]
#                 #     scope = 'function'  # TODO understand what to do
#                 #     scopenum = scope2index(scope, descr='call to {0}'.format('hack'))
#                 #     param_index = -1
#                 #     newcallspec.setmulti2(vartypes, missing_names, paramvalues, 'dummy',
#                 #                           (), scopenum, param_index)
#                 #     # remove the dummy id
#                 #     newcallspec._idlist.pop(-1)
#                 #     _calls_with_slicer2.append(newcallspec)
#                 #
#                 # separate_calls += get_calls(_calls_with_slicer2, sub_fixture)
#                 separate_calls += get_calls(_calls_with_slicer, sub_fixture)
#             return separate_calls
#         else:
#             # normal fixture. do an intelligent product (= only for callspecs that do not have this fixture)
#             newcalls = []
#             for callspec in all_the_calls or [CallSpec2(metafunc)]:
#                 # only do the product if the name is not already there
#                 if name not in callspec.params:
#                     for _callspec_to_add in normal_fixtures[name]:
#                         newcallspec = callspec.copy(metafunc)
#                         if len(_callspec_to_add._idlist) != 1:
#                             raise ValueError("each such callspec is supposed to represent a single fixture")
#                         # there is a single id, a single arg, a single param
#                         a_id = _callspec_to_add._idlist[0]
#                         argname, paramvalue = next(iter(_callspec_to_add.params.items()))
#                         scopenum = _callspec_to_add._arg2scopenum[argname]
#                         param_index = _callspec_to_add.indices[argname]
#                         newcallspec.setmulti2({argname: "params"}, [argname], [paramvalue], a_id,
#                                               _callspec_to_add.marks, scopenum, param_index)
#
#                         newcalls.append(newcallspec)
#                 else:
#                     newcalls.append(callspec)
#             return newcalls
#
#     # trigger building the list
#     all_the_calls = []
#     for name in names_required:
#         all_the_calls = get_calls(all_the_calls, name)
#
#     # finally add missing param values in each callspec
#     risky_names = {name for union_fix_defs in union_fixtures.values() for name in union_fix_defs.fixtures}
#     if len(risky_names) == 0:
#         return all_the_calls
#     else:
#         final_calls = []
#         for callspec in all_the_calls:
#             missing_names = set(risky_names) - set(callspec.params)
#             newcallspec = callspec.copy(metafunc)
#             vartypes = {argname: 'params' for argname in missing_names}
#             paramvalues = [None for argname in missing_names]
#             scope = 'function'  # TODO understand what to do
#             scopenum = scope2index(scope, descr='call to {0}'.format('hack'))
#             param_index = -1
#             newcallspec.setmulti2(vartypes, missing_names, paramvalues, 'dummy',
#                                   (), scopenum, param_index)
#             # remove the dummy id
#             newcallspec._idlist.pop(-1)
#             final_calls.append(newcallspec)
#
#         return final_calls
#
#
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
