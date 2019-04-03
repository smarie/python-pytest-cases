from functools import partial
from wrapt import ObjectProxy

import pytest

from pytest_cases.main_fixtures import UnionFixtureConfig, NOT_USED

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature


try:  # python 3.3+ type hints
    from typing import Optional, List, Tuple
    from _pytest.python import CallSpec2
except ImportError:
    pass


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
        # first call: should be an empty list
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
        calls_reactor.append_union_parametrization(union_fixture_name, union_fixture_cfg, scope=scope, **kwargs)
    else:
        # add a normal parametrization (but do not apply it)
        calls_reactor.append_product_parametrization(argnames, argvalues, indirect=indirect, ids=ids, scope=scope,
                                                     **kwargs)

    # put our object back in place - not needed anymore
    # metafunc._calls = calls_reactor


class CallsReactor:
    """
    This object replaces the list of calls that was in `metafunc._calls`.
    It behaves like a list, but it actually builds that list dynamically based on all parametrizations collected
    from the custom `metafunc.parametrize` above.

    There are therefore three steps:

     - when `metafunc.parametrize` is called, this object gets called on `add_union` or `add_param`. A parametrization
     order gets stored in `self._pending`

     - when this object is first read as a list, all parametrization orders in `self._pending` are transformed into a
     tree in `self._tree`, and `self._pending` is discarded. This is done in `create_tree_from_pending_parametrization`.

     - finally, the list is built from the tree using `self._tree.to_call_list()`. This will also be the case in
     subsequent usages of this object.

    """
    __slots__ = 'metafunc', '_pending', '_tree'

    def __init__(self, metafunc):
        self.metafunc = metafunc
        self._tree = None
        self._pending = []

    # -- methods to provising parametrization orders without executing them --

    def append_union_parametrization(self, union_fixture_name, union_fixture_cfg, scope=None, **kwargs):
        """ Adds a union to the pending operations """
        self._pending.append((SplitNode, union_fixture_name, union_fixture_cfg, scope, kwargs))

    def append_product_parametrization(self, argnames, argvalues, indirect=False, ids=None, scope=None, **kwargs):
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
        Returns the list of calls. This property relies on self._tree, that is lazily created on first access,
        based on `self.parametrizations`.
        :return:
        """
        if self._tree is None:
            # create the definitive tree.
            self.create_tree_from_pending_parametrizations()

        return self._tree.to_call_list()

    # --- tree creation (executed once the first time this object is used as a list)

    def create_tree_from_pending_parametrizations(self):
        """
        Takes all parametrization operations that are pending in `self._pending`,
        and creates a parametrization tree out of them.

        self._pending is set to None afterwards
        :return:
        """
        bak_calls = self.metafunc._calls

        # create the tree containing all the `CallSpec2` instances
        self._tree = Tree()
        names_required = list(signature(self.metafunc.function).parameters)
        for i in range(len(self._pending)):
            CallsReactor.parametrize_tree(self._tree, self.metafunc,
                                          names_required, self._pending[i], self._pending[i + 1:])
        # finalize the parametrization (all fixtures should have a value in all calls to union fixtures)
        self._tree.finalize_parametrization()

        self.metafunc._calls = bak_calls

        # forget about all parametrizations now - this wont happen again
        self._pending = None

    @staticmethod
    def parametrize_tree(node, metafunc, names_required, single_pmz, remaining_pmzs, force=None):
        """

        :param names_required:
        :param single_pmz:
        :param remaining_pmzs:
        :param force:
        :return:
        """
        # print("parametrizing node %s (with current ids %s) with %s"
        #       "" % (work_node, work_node.all_ids() if work_node is not None else None, single_pmz))

        if single_pmz[0] is SplitNode:
            # (A) a 'union' fixture
            union_fixture_name, union_fixture_cfg, scope, kwargs = single_pmz[1:]
            node.parametrize_union(metafunc, union_fixture_name, cfg=union_fixture_cfg, scope=scope, **kwargs)

            # for each newly created leaf, directly parametrize it with the fixture it is supposed to use
            force = force or (union_fixture_name in names_required)
            for leaf in node.get_leaves():
                i = CallsReactor.find_pending_param_for_fixture_name(leaf.last_selected, remaining_pmzs)
                if i is not None:
                    CallsReactor.parametrize_tree(leaf, metafunc, names_required, remaining_pmzs[i],
                                                  remaining_pmzs[i + 1:], force=force)
                # else: already done - ignore - that can happen when two unions rely on the same fixture.
        else:
            # (B) a normal parameter fixture
            argnames, argvalues, indirect, ids, scope, kwargs = single_pmz[1:]

            # if this is a fixture that is required by the function, always force the parametrization since the
            # fixture should always be set
            # otherwise, parametrize only the places where it is not already set
            force = force or (argnames in names_required)
            node.parametrize_product(metafunc, force, argnames, argvalues, indirect=indirect, ids=ids,
                             scope=scope, **kwargs)

        # print("> node %s parametrized. Current ids %s" % (work_node, work_node.all_ids()))

    @staticmethod
    def find_pending_param_for_fixture_name(f_name, remaining_parametrizations):
        """
        Returns the index of the pending parametrization with the given fixture name, or None
        """
        for i, p in enumerate(remaining_parametrizations):
            if p[1] == f_name:
                return i


class Node:
    """
    The common class shared between all tree nodes. It defines the concept of 'parent', and the base methods that all
    nodes should implement
    """
    __slots__ = ('parent', )

    def __init__(self, parent):
        self.parent = parent

    # -- tree api

    def replace_child_node(self, old_node, new_node):
        """Replace a child node with another"""
        raise NotImplementedError()

    def get_leaves(self):
        """Return all leaves under this node"""
        raise NotImplementedError()

    # -- parametrization api

    def parametrize_union(self, metafunc, union_fixture_name, cfg, scope, **kwargs):
        """Propagate a union parametrization on this node"""
        raise NotImplementedError()

    def parametrize_product(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """Propagate a normal pytest parametrization on this node: cartesian products should be made on all leafs."""
        raise NotImplementedError()

    def finalize_parametrization(self):
        """Called once at the end of parametrization, for potential last-minute actions"""
        raise NotImplementedError()

    # -- call list api
    # @property
    # def calls(self):
    #     """A property that should only be implemented by leaves"""
    #     raise NotImplementedError()

    def to_call_list(self):
        """Return the list of calls represented by the subtree at this node"""
        return [c for l in self.get_leaves() for c in l.calls]

    def all_ids(self):
        """Return the list of all test ids, for debug purposes"""
        return [c.id for c in self.to_call_list()]


class Tree(ObjectProxy):
    """
    Represents the whole tree. It is also a proxy of its root node, for convenience.
    """
    def __init__(self, root_node=None):
        ObjectProxy.__init__(self, root_node)

    # -- 'root_node' attribute

    def __getattr__(self, item):
        """ defines that 'root_node' is a valid alias for the wrapped attribute """
        if item == 'root_node':
            # item = '__wrapped__'
            return self.__wrapped__
        return ObjectProxy.__getattr__(self, item)

    def __setattr__(self, key, value):
        """ defines that 'root_node' is a valid alias for the wrapped attribute """
        if key == 'root_node':
            # key = '__wrapped__'
            self.__wrapped__ = value
        else:
            ObjectProxy.__setattr__(self, key, value)

    # -- tree implementation

    def replace_child_node(self, old_node, new_node):
        if old_node is self.root_node:
            self.root_node = new_node
        else:
            raise ValueError("internal error - should not happen")

    # -- parametrization implementation

    def parametrize_union(self, metafunc, union_fixture_name, cfg, scope, **kwargs):
        if self.root_node is None:
            # root node will be a new split node whose parent is self
            self.root_node = SplitNode.create(metafunc, union_fixture_name, parent=self, cfg=cfg, scope=scope, **kwargs)
        else:
            # the node should not be replaced - we can safely propagate
            self.root_node.parametrize_union(metafunc, union_fixture_name, cfg=cfg, scope=scope, **kwargs)

    def parametrize_product(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        if self.root_node is None:
            # root node will be a new leaf node
            self.root_node = LeafNode.create_parametrized(metafunc, argnames, argvalues, indirect=indirect, ids=ids,
                                                          scope=scope, **kwargs)
        else:
            # the node already exists and should not be replaced - we can safely propagate
            self.root_node.parametrize_product(metafunc, force, argnames, argvalues, indirect=indirect, ids=ids,
                                               scope=scope, **kwargs)


class SplitNode(Node):
    """
    Represents a set of alternatives, created because a union fixture was used.
    In each sub-branch,
    """
    __slots__ = ('alternative_nodes',)

    def __init__(self, children_nodes, parent=None):
        Node.__init__(self, parent=parent)
        self.alternative_nodes = children_nodes

    def __repr__(self):
        return "|".join(["[%s]" % n for n in self.alternative_nodes]) \
            if len(self.alternative_nodes) > 0 else "<empty_split>"

    # -- tree API

    def get_leaves(self):
        return [l for a in self.alternative_nodes for l in a.get_leaves()]

    def replace_child_node(self, old_node, new_node):
        i = self.alternative_nodes.index(old_node)
        self.alternative_nodes[i] = new_node
        assert old_node not in self.alternative_nodes

    # -- parametrization API

    def parametrize_union(self, metafunc, union_fixture_name, cfg, scope, **kwargs):
        for c in self.alternative_nodes:
            c.parametrize_union(metafunc, union_fixture_name, cfg, scope, **kwargs)

    def parametrize_product(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Parametrizes each of the partitions independently
        :return:
        """
        for child in self.alternative_nodes:
            child.parametrize_product(metafunc, force, argnames, argvalues, indirect=indirect, ids=ids, scope=scope,
                                      **kwargs)

    def finalize_parametrization(self):
        for child in self.alternative_nodes:
            child.finalize_parametrization()

    # -- alternate constructor

    @staticmethod
    def create(metafunc,
               union_fixture_name,    # type: str
               cfg,                   # type: UnionFixtureConfig
               scope,                 # type: Optional[str]
               init_leaf=None,        # type: Optional[LeafNode]
               parent=None,           # type: Optional[Node]
               **kwargs
               ):
        """
        Creates a new SplitNode for the provided union fixture configuration.

        `init_calls_list` represents the list of calls that were pre-existing on that leaf before creation, if any.

         - If it is None, the new split node will have one leaf for each possible selected fixture in the union.
         - It it is non-None, the new split node will have one leaf for each pre-existing call AND each possible
         selected fixture in the union (cartesian product).
        """
        init_selection, init_discards = None, None
        if init_leaf is None:
            init_calls_list = [[]]
        else:
            # inherit parent from leaf
            if parent is None:
                parent = init_leaf.parent

            # break down the list of calls in sublists of one element.
            init_calls_list = [[c] for c in init_leaf.calls]

            # if the leaf was a filter, remember its config
            if isinstance(init_leaf, FilteredLeafNode):
                init_selection = init_leaf.selections
                init_discards = init_leaf.discarded_fixture_names

        # create the new split node, and create one filter leaf per call per fixture to select
        new_node = SplitNode([], parent=parent)
        for init_calls in init_calls_list:
            for i, sub_fix in enumerate(cfg.fixtures):
                new_leaf = FilteredLeafNode(metafunc, union_fixture_name, sub_fix,
                                            cfg.fixtures[0:i] + cfg.fixtures[(i + 1):], initial_calls=init_calls,
                                            initial_selections=init_selection, initial_discarded_names=init_discards,
                                            scope=scope, parent=new_node, **kwargs)
                new_node.alternative_nodes.append(new_leaf)

        return new_node


class LeafNode(Node):
    """
    Represents a "normal" set of calls. When this set of calls gets parametrized, the behaviour is exactly the same
    than in normal pytest: a cartesian product is made to produce the new list of calls.

    If no union fixtures are used in a test, the tree will be a single `LeafNode`.
    """
    __slots__ = ('calls', )

    def __init__(self, calls, parent=None):
        Node.__init__(self, parent=parent)
        self.calls = calls

    # -- alternate constructor

    @staticmethod
    def create_parametrized(metafunc, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Creates a LeafNode and parametrize it according to the provided arguments.
        """
        new = LeafNode([])
        new.parametrize_product(metafunc, True, argnames, argvalues, indirect=indirect, ids=ids, scope=scope, **kwargs)
        return new

    # -- tree api

    def get_leaves(self):
        return [self]

    # -- parametrization api

    def parametrize_union(self, metafunc, union_fixture_name, cfg, scope, **kwargs):
        """
        Replaces the current node with a split node created by applying the union on all calls in this leaf.
        """
        new_node = SplitNode.create(metafunc, union_fixture_name, cfg=cfg, scope=scope, init_leaf=self, **kwargs)
        self.parent.replace_child_node(self, new_node)

    def parametrize_product(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Standard pytest parametrization: do the cartesian product of the parameters with the calls that are already
        there.

        The difference with normal pytest is that the `metafunc` provided is not changed by this method. It is just
        used as a convenient way to call `parametrize`

        Note: 'force' is a keyword for the subclass, it is not used here.
        :return:
        """
        bak = metafunc._calls
        metafunc._calls = self.calls
        # since we replaced the `parametrize` method on `metafunc` we have to call super here
        metafunc.__class__.parametrize(metafunc, argnames, argvalues, indirect=indirect, ids=ids, scope=scope,
                                       **kwargs)
        self.calls = metafunc._calls
        metafunc._calls = bak

    def finalize_parametrization(self):
        """Nothing special to do"""
        pass

    # -- misc

    def discard_last_id(self):
        """Remove the last id in all callspecs in this node"""
        for callspec in self.calls:
            callspec._idlist.pop(-1)


class FilteredLeafNode(LeafNode):
    """
    Represents a set of calls for which at least one union fixture has been parametrized.
    In this case, we have to remember the fixture in the union that is active in this set of calls
    (`selected_fixture_name`) and the other fixtures in the union, that are not active (`discarded_fixture_names`).

    Two things make this class a bit complex:

     - several union fixtures can be used. So we need a way to 'inherit' the selected fixtures and discarded fixtures
     from the parent nodes.
     -

    """
    __slots__ = ('metafunc', 'union_fixture_name', 'selections', 'discarded_fixture_names')

    def __init__(self,
                 metafunc,
                 union_fixture_name,            # type: str
                 selected_fixture_name,         # type: str
                 discarded_fixture_names,       # type: List[str]
                 initial_calls=None,            # type: Optional[List[CallSpec2]]
                 initial_selections=None,       # type: Optional[List[Tuple[str, str]]]
                 initial_discarded_names=None,  # type: Optional[List[str]]
                 parent=None,                   # type: Optional[Node]
                 scope=None,
                 **kwargs):
        """
        Constructor with a possible initial list of calls and initial selections.
        Once created the node is parametrized with the "union" fixture.
        """
        # create the node with existing calls
        LeafNode.__init__(self, initial_calls, parent=parent)

        self.metafunc = metafunc
        self.union_fixture_name = union_fixture_name

        # save the fixture names that are selected/discarded
        self.selections = [(union_fixture_name, selected_fixture_name)]
        self.discarded_fixture_names = discarded_fixture_names
        if initial_selections is not None:
            self.selections = initial_selections + self.selections
        if initial_discarded_names is not None:
            self.discarded_fixture_names = initial_discarded_names + self.discarded_fixture_names

        # parametrize with the union node
        # _id = '%s=%s' % (union_fixture_name, selected_fixture_name)
        _id = '%s' % selected_fixture_name
        self.parametrize_product(metafunc, False, union_fixture_name, [selected_fixture_name], indirect=True,
                         ids=[_id], scope=scope, **kwargs)

        # remove the id
        # self.discard_last_id()

    def __repr__(self):
        return '&'.join(['%s=%s' % s for s in self.selections])\
            if len(self.selections) > 0 else "<empty_filtered_leaf>"

    # -- misc

    @property
    def last_selected(self):
        return self.selections[-1][1]

    # -- parametrization api

    def parametrize_product(self, metafunc, force, argnames, argvalues, indirect, ids, scope, **kwargs):
        """
        Same than super: this is the standard pytest parametrization of calls, doing a cartesian product of the new
        parameters with the ones already in place.

        The difference with super is that

         - there is a protection against multiple parametrizations. if the parameter has already been used on this node,
           no new parametrization is triggered. This happens when typically the parameter is one of the fixtures
           selected in this node: in this case the `CallsReactor` applies it once on this node just after node creation,
           and reapplies it normally later on the whole tree.

         - the `force` parameter has an effect: if force is set to True, parametrization will always happen even if the
           corresponding parameter is a discarded fixture. This typically happens if that fixture is needed by
           something else (the test itself, or another fixture). Otherwise, parametrization will only be done if the
           argname is not a discarded fixture.

        :return:
        """
        if len(self.calls) > 0 and argnames in self.calls[0].params:
            # already set.
            pass
        elif force or (argnames not in self.discarded_fixture_names):
            LeafNode.parametrize_product(self, metafunc, force, argnames, argvalues, indirect=indirect, ids=ids,
                                         scope=scope, **kwargs)

    def finalize_parametrization(self):
        """
        If there are fixture names that were discarded on the way,
        we have to give them a value - even if they will not actually be used.
        """
        for missing in self.discarded_fixture_names:
            if missing not in self.calls[0].params:
                # parametrize with value NOT_USED
                self.parametrize_product(self.metafunc, True, missing, [NOT_USED], indirect=True,
                                 ids=['_'], scope=None)

                # remove the corresponding id element since the fixture is not used at all
                self.discard_last_id()
