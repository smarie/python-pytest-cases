from collections import OrderedDict, namedtuple
from copy import copy
from distutils.version import LooseVersion
from functools import partial
from warnings import warn

import pytest

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature  # noqa

try:  # python 3.3+ type hints
    from typing import List, Tuple, Union, Iterable, MutableMapping  # noqa
    from _pytest.python import CallSpec2
except ImportError:
    pass

from .common_mini_six import string_types
from .common_pytest import get_pytest_nodeid, get_pytest_function_scopenum, is_function_node, get_param_names, \
    get_pytest_scopenum, get_param_argnames_as_list
from .fixture_core1_unions import NOT_USED, is_fixture_union_params, UnionFixtureAlternative


_DEBUG = False


# @hookspec(firstresult=True)
# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_collection(session):
    # override the fixture manager's method
    session._fixturemanager.getfixtureclosure = partial(getfixtureclosure, session._fixturemanager)  # noqa


class FixtureDefsCache(object):
    """
    The object plays a role of 'cache' for fixture definitions.
    """
    __slots__ = 'fm', 'nodeid', 'cached_fix_defs'

    def __init__(self, fm, nodeid):
        self.fm = fm
        self.nodeid = nodeid
        self.cached_fix_defs = dict()

    def get_fixture_defs(self, fixname):
        try:
            # try to retrieve it from cache
            fixdefs = self.cached_fix_defs[fixname]
        except KeyError:
            # otherwise get it and store for next time
            fixdefs = self.fm.getfixturedefs(fixname, self.nodeid)
            self.cached_fix_defs[fixname] = fixdefs

        return fixdefs


class FixtureClosureNode(object):
    __slots__ = 'parent', 'fixture_defs', \
                'split_fixture_name', 'split_fixture_discarded_names', 'children', \
                '_as_list', 'all_fixture_defs', 'fixture_defs_mgr'

    def __init__(self,
                 fixture_defs_mgr=None,   # type: FixtureDefsCache
                 parent_node=None         # type: FixtureClosureNode
                 ):
        if fixture_defs_mgr is None:
            if parent_node is None:
                raise ValueError()
            fixture_defs_mgr = parent_node.fixture_defs_mgr
        else:
            assert isinstance(fixture_defs_mgr, FixtureDefsCache)

        self.fixture_defs_mgr = fixture_defs_mgr
        self.parent = parent_node

        # these will be set after closure has been built
        self.fixture_defs = None
        self.split_fixture_name = None
        self.split_fixture_discarded_names = []
        self.children = OrderedDict()  # type: MutableMapping[str, FixtureClosureNode]

        # this will be created after the first time the object is converted to a list (cache)
        self._as_list = None
        self.all_fixture_defs = None

    # ------ tree
    def get_leaves(self):
        if self.has_split():
            return [n for c in self.children.values() for n in c.get_leaves()]
        else:
            return [self]
    # ------

    def to_str(self, indent_nb=0, with_children=True, with_discarded=True):
        """
        Provides a string representation, either with all the subtree (default) or without (with_children=False)

        You can also remove the "discarded" information for clarity with with_discarded=False

        :param indent_nb:
        :param with_children:
        :param with_discarded:
        :return:
        """

        indent = " " * indent_nb

        if not self.is_closure_built():
            str_repr = "<pending, incomplete>"
        else:
            str_repr = "%s(%s)" % (indent, ",".join([("%s" % f) for f in self.fixture_defs.keys()]))
            if with_discarded:
                str_repr += "  (discarded: %s)" % self.split_fixture_discarded_names

        if self.has_split() and with_children:
            children_str_prefix = "\n%s - " % indent
            children_str = children_str_prefix + children_str_prefix.join([c.to_str(indent_nb=indent_nb + 1)
                                                                           for c in self.children.values()])
            str_repr = str_repr + " split: " + self.split_fixture_name + children_str

        return str_repr

    def __repr__(self):
        return self.to_str()

    # ---- list facade

    def __iter__(self):
        return iter(self.to_list())

    def __getitem__(self, item):
        return self.to_list()[item]

    def __setitem__(self, key, value):
        # This is called in Pytest 4+.
        if self.has_split():
            # TODO how should we behave ?
            warn("WARNING the new order is not taken into account !!")
        else:
            self.to_list()[key] = value

    def append(self, item):
        """
        This is now supported: we simply update the closure with the new item.
        `self.all_fixture_defs` and `self._as_list` are updated on the way
        so the resulting facades used by pytest are consistent after the update.

        :param item:
        :return:
        """
        self.build_closure((item, ))

    def insert(self, index, object):  # noqa
        warn("WARNING some code tries to insert an item in the fixture tree, this will be IGNORED !! "
             "Item: %s, Index: %s" % (index, object))

    def pop(self, index):  # noqa
        warn("WARNING some code tries to pop an item from the fixture tree, this will be IGNORED !! Index: %s" % index)

    def extend(self, iterable):  # noqa
        if len(iterable) > 0:
            warn("WARNING some code tries to extend the fixture tree, this will be IGNORED !! Iterable: %s" % iterable)

    def index(self, *args):
        return self.to_list().index(*args)

    def to_list(self):
        """
        Converts self to a list to get all fixture names, and caches the result.
        :return:
        """
        if self._as_list is None:
            # crawl the tree to get the list of unique fixture names
            fixturenames_closure = self._to_list()

            if LooseVersion(pytest.__version__) >= LooseVersion('3.5.0'):
                # sort by scope
                def sort_by_scope(arg_name):
                    try:
                        fixturedefs = self.get_all_fixture_defs()[arg_name]
                    except KeyError:
                        return get_pytest_function_scopenum()
                    else:
                        return fixturedefs[-1].scopenum
                fixturenames_closure.sort(key=sort_by_scope)

            self._as_list = fixturenames_closure

        return self._as_list

    def _to_list(self):
        """ Returns a list of all fixture names used (with no redundancy) """

        lst = []
        self._append_to(lst)

        # eliminate redundancy
        unique_lst = _make_unique(lst)

        # TODO remove for efficiency
        assert set(unique_lst) == set(lst)

        return unique_lst

    def _append_to(self, lst):
        """Appends all fixture names of this subtree to the given list"""

        # first append the fixture names
        lst += list(self.fixture_defs.keys())

        # then if there is a split at this node
        if self.has_split():
            # add the split fixture > not needed anymore
            # lst.append(self.split_fixture_name)

            # add all children
            for c in self.children.values():
                c._append_to(lst)

    # ----
    def get_all_fixture_defs(self):
        if self.all_fixture_defs is None:
            # collect
            self.all_fixture_defs = self._get_all_fixture_defs()

        return self.all_fixture_defs

    def _get_all_fixture_defs(self):
        all_fix_defs = OrderedDict()
        for k, v in self.fixture_defs.items():
            if v is not None:
                all_fix_defs[k] = v
        for c in self.children.values():
            all_fix_defs.update(c.get_all_fixture_defs())
        return all_fix_defs

    # ---- utils to build the closure

    def build_closure(self,
                      initial_fixture_names,  # type: Iterable[str]
                      ignore_args=()
                      ):
        """
        Updates this Node with the fixture names provided as argument.
        Fixture names and definitions will be stored in self.fixture_defs.

        If some fixtures are Union fixtures, this node will become a "split" node
        and have children. If new fixtures are added to the closure after that,
        they will be added to the child nodes rather than self.

        Note: when this method is used on an existing (already filled) root node,
        all of its internal structures (self._as_list and self.all_fixture_defs) are updated accordingly so that the
        facades used by pytest are still consistent.

        :param initial_fixture_names:
        :param ignore_args: arguments to keep in the names but not to put in the fixture defs, because they correspond
            "direct parametrize"
        :return:
        """
        self._build_closure(self.fixture_defs_mgr, initial_fixture_names, ignore_args=ignore_args)

        # update fixture defs
        if self.all_fixture_defs is None:
            self.all_fixture_defs = self._get_all_fixture_defs()
        else:
            self.all_fixture_defs.update(self._get_all_fixture_defs())

        # mark the fixture list as to be rebuilt (automatic next time one iterates on self)
        self._as_list = None

    def is_closure_built(self):
        return self.fixture_defs is not None

    def already_knows_fixture(self, fixture_name):
        """ Return True if this fixture is known by this node or one of its parents """
        if fixture_name in self.fixture_defs:
            return True
        elif self.parent is None:
            return False
        else:
            return self.parent.already_knows_fixture(fixture_name)

    def _build_closure(self,
                       fixture_defs_mgr,       # type: FixtureDefsCache
                       initial_fixture_names,  # type: Iterable[str]
                       ignore_args
                       ):
        """

        :param fixture_defs_mgr:
        :param initial_fixture_names:
        :param ignore_args: arguments to keep in the names but not to put in the fixture defs
        :return: nothing (the input arg2fixturedefs is modified)
        """

        # Grab all dependencies of all fixtures present at this node and add them to either this or to nodes below.

        # -- first switch this object from 'pending' to 'under construction' if needed
        # (indeed we now authorize and use the possibility to call this twice. see split() )
        if self.fixture_defs is None:
            self.fixture_defs = OrderedDict()

        # -- then for all pending, add them with their dependencies
        pending_fixture_names = list(initial_fixture_names)
        while len(pending_fixture_names) > 0:
            fixname = pending_fixture_names.pop(0)

            # if the fixture is already known in this node or above, do not care
            if self.already_knows_fixture(fixname):
                continue

            # new ignore_args option in pytest 4.6+
            if fixname in ignore_args:
                self.add_required_fixture(fixname, None)
                continue

            # else grab the fixture definition(s) for this fixture name for this test node id
            fixturedefs = fixture_defs_mgr.get_fixture_defs(fixname)
            if not fixturedefs:
                # fixture without definition: add it
                self.add_required_fixture(fixname, None)
                continue
            else:
                # the actual definition is the last one
                _fixdef = fixturedefs[-1]
                _params = _fixdef.params

                if _params is not None and is_fixture_union_params(_params):
                    # create an UNION fixture

                    # transform the _params into a list of names
                    alternative_f_names = UnionFixtureAlternative.to_list_of_fixture_names(_params)

                    # TO DO if only one name, simplify ? >> No, we leave such "optimization" to the end user

                    # if there are direct dependencies that are not the union members, add them to pending
                    non_member_dependencies = [f for f in _fixdef.argnames if f not in alternative_f_names]
                    pending_fixture_names += non_member_dependencies

                    # propagate WITH the pending
                    self.split_and_build(fixture_defs_mgr, fixname, fixturedefs, alternative_f_names,
                                         pending_fixture_names, ignore_args=ignore_args)

                    # empty the pending because all of them have been propagated on all children with their dependencies
                    pending_fixture_names = []
                    continue

                else:
                    # normal fixture
                    self.add_required_fixture(fixname, fixturedefs)

                    # add all dependencies in the to do list
                    dependencies = _fixdef.argnames
                    # - append: was pytest default
                    # pending_fixture_names += dependencies
                    # - prepend: makes much more sense
                    pending_fixture_names = list(dependencies) + pending_fixture_names
                    continue

    # ------ tools to add new fixture names during closure construction

    def add_required_fixture(self, new_fixture_name, new_fixture_defs):
        """Add some required fixture names to this node. Returns True if new fixtures were added here (not in child)"""
        if self.already_knows_fixture(new_fixture_name):
            return
        elif not self.has_split():
            # add_required_fixture locally
            if new_fixture_name not in self.fixture_defs:
                self.fixture_defs[new_fixture_name] = new_fixture_defs
        else:
            # add_required_fixture in each child
            for c in self.children.values():
                c.add_required_fixture(new_fixture_name, new_fixture_defs)

    def split_and_build(self,
                        fixture_defs_mgr,           # type: FixtureDefsCache
                        split_fixture_name,         # type: str
                        split_fixture_defs,         # type: Tuple[FixtureDefinition]  # noqa
                        alternative_fixture_names,  # type: List[str]
                        pending_fixtures_list,      #
                        ignore_args
                        ):
        """ Declares that this node contains a union with alternatives (child nodes=subtrees) """

        if self.has_split():
            raise ValueError("This should not happen anymore")
            # # propagate the split on the children: split each of them
            # for n in self.children.values():
            #     n.split_and_build(fm, nodeid, split_fixture_name, split_fixture_defs, alternative_fixture_names)
        else:
            # add the split (union) name to known fixtures
            self.add_required_fixture(split_fixture_name, split_fixture_defs)

            # remember it
            self.split_fixture_name = split_fixture_name

            # create the child nodes
            for f in alternative_fixture_names:
                # create the child node
                new_c = FixtureClosureNode(parent_node=self)
                self.children[f] = new_c

                # set the discarded fixture names
                new_c.split_fixture_discarded_names = [g for g in alternative_fixture_names if g != f]

                # perform the propagation:
                # (a) first propagate all child's dependencies, (b) then the ones required by parent
                # we need to do both at the same time in order to propagate the "pending for child" on all subbranches
                pending_for_child = [f] + pending_fixtures_list
                new_c._build_closure(fixture_defs_mgr, pending_for_child, ignore_args=ignore_args)

    def has_split(self):
        return self.split_fixture_name is not None

    def get_not_always_used(self):
        """Returns the list of fixtures used by this subtree, that are not always used"""
        results_list = []

        # initial list is made of fixtures that are in the children
        initial_list = self.gather_all_required(include_parents=False)

        for c in self.get_leaves():
            j = 0
            for i in range(len(initial_list)):
                fixture_name = initial_list[j]
                if fixture_name not in c.gather_all_required():
                    del initial_list[j]
                    results_list.append(fixture_name)
                else:
                    j += 1

        return results_list

    def gather_all_required(self, include_children=True, include_parents=True):
        """
        Returns a list of all fixtures required by the subtree at this node

        :param include_children:
        :param include_parents:
        :return:
        """
        # first the fixtures required by this node
        required = list(self.fixture_defs.keys())

        # then the ones required by the parents
        if include_parents and self.parent is not None:
            required = required + self.parent.gather_all_required(include_children=False)

        # then the ones from all the children
        if include_children:
            for child in self.children.values():
                required = required + child.gather_all_required(include_parents=False)

        return required

    def requires(self, fixturename):
        """
        Returns True if the fixture with this name is required by the subtree at this node
        :param fixturename:
        :return:
        """
        return fixturename in self.gather_all_required()

    def gather_all_discarded(self):
        """
        Returns a list of all fixture names discarded during splits from the parent node down to this node.
        Note: this does not include the split done at this node if any, nor all of its subtree.
        :return:
        """
        discarded = list(self.split_fixture_discarded_names)
        if self.parent is not None:
            discarded = discarded + self.parent.gather_all_discarded()

        return discarded

    # ------ tools to see the tree as a list of alternatives

    def print_alternatives(self):
        return FixtureClosureNode.print_alternatives_list(*self.get_alternatives())

    @staticmethod
    def print_alternatives_list(filters_list, fixtures_list):
        for f, p in zip(filters_list, fixtures_list):
            print(f, p)

    def get_alternatives(self):
        """
        Returns the alternatives
        - a list of dictionaries union_fixture_name: value representing the filters on this alternative
        - a list of tuples of fixture names used by each alternative
        - a list of tuples of discarded fixture names in each alternative
        :return:
        """
        if self.has_split():
            partitions_list = []
            filters_list = []
            discarded_list = []
            for k, c in self.children.items():
                child_filters_dct, child_partitions, child_discarded = c.get_alternatives()
                for f_dct, p, d in zip(child_filters_dct, child_partitions, child_discarded):
                    # append a partition for this child:
                    # - filter
                    _f_dct = f_dct.copy()
                    _f_dct[self.split_fixture_name] = k
                    filters_list.append(_f_dct)
                    # - fixtures used
                    partitions_list.append(_make_unique(list(self.fixture_defs.keys()) + p))
                    # - fixtures not used.
                    discarded_list.append(_make_unique(self.split_fixture_discarded_names
                                                       + [df for df in d if df not in self.fixture_defs.keys()]))

            return filters_list, partitions_list, discarded_list
        else:
            # return a single partition containing all fixture names
            return [dict()], [list(self.fixture_defs.keys())], [list(self.split_fixture_discarded_names)]


def merge(new_items, into_list):
    """
    Appends items from `new_items` into `into_list`, only if they are not already there.
    :param new_items:
    :param into_list:
    :return:
    """
    at_least_one_added = False
    for item in new_items:
        if item not in into_list:
            into_list.append(item)
            at_least_one_added = True
    return at_least_one_added


def getfixtureclosure(fm, fixturenames, parentnode, ignore_args=()):

    # first retrieve the normal pytest output for comparison
    kwargs = dict()
    if LooseVersion(pytest.__version__) >= LooseVersion('4.6.0'):
        # new argument "ignore_args" in 4.6+
        kwargs['ignore_args'] = ignore_args

    if LooseVersion(pytest.__version__) >= LooseVersion('3.7.0'):
        # three outputs
        initial_names, ref_fixturenames, ref_arg2fixturedefs = \
            fm.__class__.getfixtureclosure(fm, fixturenames, parentnode, **kwargs)
    else:
        # two outputs
        ref_fixturenames, ref_arg2fixturedefs = fm.__class__.getfixtureclosure(fm, fixturenames, parentnode)

    # now let's do it by ourselves.
    parentid = parentnode.nodeid

    # Create closure
    # -- auto-use fixtures
    _init_fixnames = fm._getautousenames(parentid)  # noqa

    # -- required fixtures/params.
    # ********* fix the order of initial fixtures: indeed this order may not be the right one ************
    # this only works when pytest version is > 3.4, otherwise the parent node is a Module
    if is_function_node(parentnode):
        # grab all the parametrization on that node and fix the order.
        # Note: on pytest >= 4 the list of param_names is probably the same than the `ignore_args` input
        param_names = get_param_names(parentnode)

        sorted_fixturenames = sort_according_to_ref_list(fixturenames, param_names)
        # **********
        # merge the fixture names in correct order into the _init_fixnames
        merge(sorted_fixturenames, _init_fixnames)
    else:
        # we cannot sort yet - merge the fixture names into the _init_fixnames
        merge(fixturenames, _init_fixnames)
        sorted_fixturenames = []

    # Finally create the closure tree
    if _DEBUG:
        print("Creating closure for %s:" % parentid)

    fixture_defs_mger = FixtureDefsCache(fm, parentid)
    fixturenames_closure_node = FixtureClosureNode(fixture_defs_mgr=fixture_defs_mger)
    fixturenames_closure_node.build_closure(_init_fixnames, ignore_args=ignore_args)

    if _DEBUG:
        print("Closure for %s completed:" % parentid)
        print(fixturenames_closure_node)

    # sort the fixture names (note: only in recent pytest)
    fixturenames_closure_node.to_list()

    # FINALLY compare with the previous behaviour TODO remove when in 'production' ?
    arg2fixturedefs = fixturenames_closure_node.get_all_fixture_defs()
    # if len(ignore_args) == 0:
    assert dict(arg2fixturedefs) == ref_arg2fixturedefs
    # if fixturenames_closure_node.has_split():
    #     # order might be changed
    #     assert set((str(f) for f in fixturenames_closure_node)) == set(ref_fixturenames)
    # else:
    #     # same order
    #     if len(p_markers) < 2:
    #         assert list(fixturenames_closure_node) == ref_fixturenames
    #     else:
    # NOW different order happens all the time because of the "prepend" strategy in the closure building
    # which makes much more sense/intuition.
    assert set((str(f) for f in fixturenames_closure_node)) == set(ref_fixturenames)

    # and store our closure in the node
    # note as an alternative we could return a custom object in place of the ref_fixturenames
    # store_union_closure_in_node(fixturenames_closure_node, parentnode)

    if LooseVersion(pytest.__version__) >= LooseVersion('3.7.0'):
        our_initial_names = sorted_fixturenames  # initial_names
        return our_initial_names, fixturenames_closure_node, arg2fixturedefs
    else:
        return fixturenames_closure_node, arg2fixturedefs


# ------------ hack to store and retrieve our custom "closure" object
# def store_union_closure_in_node(fixturenames_closure_node, parentnode):
#     parentnode.advanced_fixture_closure = fixturenames_closure_node


def retrieve_union_closure_from_metafunc(metafunc):
    return metafunc.fixturenames
# ---------------------------------------


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


class UnionParamz(namedtuple('UnionParamz', ['union_fixture_name', 'alternative_names', 'ids', 'scope', 'kwargs'])):
    """ Represents some parametrization to be applied, for a union fixture """

    __slots__ = ()

    def __str__(self):
        return "[UNION] %s=[%s], ids=%s, scope=%s, kwargs=%s" \
               "" % (self.union_fixture_name, ','.join([str(a) for a in self.alternative_names]),
                     self.ids, self.scope, self.kwargs)


class NormalParamz(namedtuple('NormalParamz', ['argnames', 'argvalues', 'indirect', 'ids', 'scope', 'kwargs'])):
    """ Represents some parametrization to be applied """

    __slots__ = ()

    def __str__(self):
        return "[NORMAL] %s=[%s], indirect=%s, ids=%s, scope=%s, kwargs=%s" \
               "" % (self.argnames, self.argvalues, self.indirect, self.ids, self.scope, self.kwargs)


def parametrize(metafunc, argnames, argvalues, indirect=False, ids=None, scope=None, **kwargs):
    """
    This alternate implementation of metafunc.parametrize creates a list of calls that is not just the cartesian
    product of all parameters (like the pytest behaviour).

    Instead, it offers an alternate list of calls takinginto account all union fixtures.

    For this, it replaces the `metafunc._calls` attribute with a `CallsReactor` instance, and feeds it with all
    parameters and parametrized fixtures independently (not doing any cross-product).

    The resulting `CallsReactor` instance is then able to dynamically behave like the correct list of calls,
    lazy-creating that list when it is used.
    """
    # create our special container object if needed
    if not isinstance(metafunc._calls, CallsReactor):  # noqa
        # first call: should be an empty list
        if len(metafunc._calls) > 0:  # noqa
            raise ValueError("This should not happen - please file an issue")
        metafunc._calls = CallsReactor(metafunc)

    # grab it
    calls_reactor = metafunc._calls  # noqa

    # detect union fixtures
    if is_fixture_union_params(argvalues):
        if ',' in argnames or not isinstance(argnames, string_types):
            raise ValueError("Union fixtures can not be parametrized")
        union_fixture_name = argnames
        union_fixture_alternatives = argvalues
        if indirect is False or len(kwargs) > 0:
            raise ValueError("indirect cannot be set on a union fixture, as well as unknown kwargs")

        # add a union parametrization in the queue (but do not apply it now)
        calls_reactor.append(UnionParamz(union_fixture_name, union_fixture_alternatives, ids, scope, kwargs))
    else:
        # add a normal parametrization in the queue (but do not apply it now)
        calls_reactor.append(NormalParamz(argnames, argvalues, indirect, ids, scope, kwargs))

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
    __slots__ = 'metafunc', '_pending', '_call_list'

    def __init__(self, metafunc):
        self.metafunc = metafunc
        self._pending = []
        self._call_list = None

    # -- methods to provising parametrization orders without executing them --

    def append(self,
               parametrization  # type: Union[UnionParamz, NormalParamz]
               ):
        self._pending.append(parametrization)

    def print_parametrization_list(self):
        """Helper method to print all pending parametrizations in this reactor """
        print("\n".join([str(p) for p in self._pending]))

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
        if self._call_list is None:
            # create the definitive tree.
            self.create_call_list_from_pending_parametrizations()

        return self._call_list

    # --- tree creation (executed once the first time this object is used as a list)

    def create_call_list_from_pending_parametrizations(self):
        """
        Takes all parametrization operations that are pending in `self._pending`,
        and creates a parametrization tree out of them.

        self._pending is set to None afterwards
        :return:
        """
        # temporarily remove self from the _calls field, we'll need to change it
        bak_calls = self.metafunc._calls
        assert bak_calls is self

        # grab the fixtures closure tree created previously (see getfixtureclosure above)
        fix_closure_tree = retrieve_union_closure_from_metafunc(self.metafunc)

        # ------ parametrize the calls --------
        # create a dictionary of pending things to parametrize, and only keep the first parameter in case of several
        pending_items = [(get_param_argnames_as_list(p[0])[0], p) for p in self._pending]
        pending = OrderedDict(pending_items)

        if _DEBUG:
            print()
            print("---- pending parametrization ----")
            self.print_parametrization_list()
            print("---------------------------------")
            print()
            print("Applying all of them in the closure tree nodes:")

        calls, nodes = self._process_node(fix_closure_tree, pending.copy(), [])

        self._cleanup_calls_list(fix_closure_tree, calls, nodes, pending)

        if _DEBUG:
            print("\n".join(["%s[%s]: funcargs=%s, params=%s" % (get_pytest_nodeid(self.metafunc),
                                                                 c.id, c.funcargs, c.params)
                             for c in calls]))
            print()

        self._call_list = calls

        # put back self as the _calls facade
        self.metafunc._calls = bak_calls

        # forget about all parametrizations now - this wont happen again
        self._pending = None

    def _cleanup_calls_list(self, fix_closure_tree, calls, nodes, pending):
        """
        Cleans the calls list so that all calls contain a value for all parameters. This is basically
        about adding "NOT_USED" parametrization everywhere relevant.

        :param calls:
        :param nodes:
        :param pending:
        :return:
        """

        nb_calls = len(calls)
        if nb_calls != len(nodes):
            raise ValueError("This should not happen !")

        # function_scope_num = get_pytest_function_scopenum()

        for i in range(nb_calls):
            c, n = calls[i], nodes[i]

            # A/ set to "not used" all parametrized fixtures that were not used in some branches
            for fixture, p_to_apply in pending.items():
                if fixture not in c.params and fixture not in c.funcargs:
                    # parametrize with a single "not used" value and discard the id
                    if isinstance(p_to_apply, UnionParamz):
                        c_with_dummy = self._parametrize_calls([c], p_to_apply.union_fixture_name, [NOT_USED],
                                                               indirect=True, discard_id=True,
                                                               scope=p_to_apply.scope, **p_to_apply.kwargs)
                    else:
                        _nb_argnames = len(get_param_argnames_as_list(p_to_apply.argnames))
                        if _nb_argnames > 1:
                            _vals = [(NOT_USED,) * _nb_argnames]
                        else:
                            _vals = [NOT_USED]
                        c_with_dummy = self._parametrize_calls([c], p_to_apply.argnames, _vals,
                                                               indirect=p_to_apply.indirect, discard_id=True,
                                                               scope=p_to_apply.scope, **p_to_apply.kwargs)
                    assert len(c_with_dummy) == 1
                    calls[i] = c_with_dummy[0]
                    c = calls[i]

            # B/ some non-parametrized fixtures may also need to be explicitly deactivated in some callspecs
            # otherwise they will be setup/teardown.
            #
            # For this we use a dirty hack: we add a parameter with they name in the callspec, it seems to be propagated
            # in the `request`. TODO is there a better way?
            # for fixture in list(fix_closure_tree):
            # for fixture_name, fixdef in self.metafunc._arg2fixturedefs.items():
            for fixture_name in fix_closure_tree.get_not_always_used():
                try:
                    fixdef = self.metafunc._arg2fixturedefs[fixture_name]  # noqa
                except KeyError:
                    continue  # dont raise any error here and let pytest say "not found"
                    
                if fixture_name not in c.params and fixture_name not in c.funcargs:
                    if not n.requires(fixture_name):
                        # explicitly add it as discarded by creating a parameter value for it.
                        c.params[fixture_name] = NOT_USED
                        c.indices[fixture_name] = 1
                        c._arg2scopenum[fixture_name] = get_pytest_scopenum(fixdef[-1].scope)  # noqa
                    else:
                        # explicitly add it as active
                        c.params[fixture_name] = 'used'
                        c.indices[fixture_name] = 0
                        c._arg2scopenum[fixture_name] = get_pytest_scopenum(fixdef[-1].scope)  # noqa

    def _parametrize_calls(self, init_calls, argnames, argvalues, discard_id=False, indirect=False, ids=None,
                           scope=None, **kwargs):
        """Parametrizes the initial `calls` with the provided information and returns the resulting new calls"""

        # make a backup so that we can restore the metafunc at the end
        bak = self.metafunc._calls

        # place the initial calls on the metafunc
        self.metafunc._calls = init_calls if init_calls is not None else []

        # parametrize the metafunc. Since we replaced the `parametrize` method on `metafunc` we have to call super
        self.metafunc.__class__.parametrize(self.metafunc, argnames, argvalues, indirect=indirect, ids=ids,
                                            scope=scope, **kwargs)

        # extract the result
        new_calls = self.metafunc._calls

        # If the user wants to discard the newly created id, remove the last id in all these callspecs in this node
        if discard_id:
            for callspec in new_calls:
                callspec._idlist.pop(-1)  # noqa

        # restore the metafunc and return the new calls
        self.metafunc._calls = bak
        return new_calls

    def _process_node(self, current_node, pending, calls):
        """
        Routine to apply all the parametrization orders in `pending` that are relevant to `current_node`,
        to the `calls` (a list of pytest CallSpec2).

        It returns a tuple containing a list of calls and a list of same length containing which leaf node each one
        corresponds to.

        :param current_node: the closure tree node we're focusing on
        :param pending: a list of parametrization orders to apply
        :param calls:
        :return: a tuple (calls, nodes) of two lists of the same length. So that for each CallSpec calls[i], you can see
            the corresponding leaf node in nodes[i]
        """

        # (1) first apply all non-split fixtures at this node
        fixtures_at_this_node = [f for f in current_node.fixture_defs.keys()
                                 if f is not current_node.split_fixture_name]

        # dirty hack if we want to preserve pytest legacy order when there are no children
        # if current_node.parent is None and not current_node.has_split():
        #     # legacy compatibility: use pytest parametrization order even if it is wrong
        #     # see https://github.com/pytest-dev/pytest/issues/5054
        #
        # else:
        #     # rather trust the order we computed from the closure
        #     fixtures_to_process = fixtures_at_this_node

        for fixturename in fixtures_at_this_node:
            try:
                # pop it from pending - do not rely the order in pending but rather the order in the closure node
                p_to_apply = pending.pop(fixturename)
            except KeyError:
                # not a parametrized fixture
                continue
            else:
                if isinstance(p_to_apply, UnionParamz):
                    raise ValueError("This should not happen !")
                elif isinstance(p_to_apply, NormalParamz):
                    # ******** Normal parametrization **********
                    if _DEBUG:
                        print("[Node %s] Applying parametrization for NORMAL %s"
                              "" % (current_node.to_str(with_children=False, with_discarded=False),
                                    p_to_apply.argnames))

                    calls = self._parametrize_calls(calls, p_to_apply.argnames, p_to_apply.argvalues,
                                                    indirect=p_to_apply.indirect, ids=p_to_apply.ids,
                                                    scope=p_to_apply.scope, **p_to_apply.kwargs)
                else:
                    raise TypeError("Invalid parametrization type: %s" % p_to_apply.__class__)

        # (2) then if there is a split apply it, otherwise return
        if not current_node.has_split():
            nodes = [current_node] * len(calls)
            return calls, nodes
        else:
            try:
                # pop it from pending - do not trust the order in pending.
                p_to_apply = pending.pop(current_node.split_fixture_name)
            except KeyError:
                # not a parametrized fixture
                raise ValueError("Error: fixture union parametrization not present")
            else:
                if isinstance(p_to_apply, NormalParamz):
                    raise ValueError("This should not happen !")
                elif isinstance(p_to_apply, UnionParamz):
                    # ******** Union parametrization **********
                    if _DEBUG:
                        print("[Node %s] Applying parametrization for UNION %s"
                              "" % (current_node.to_str(with_children=False, with_discarded=False),
                                    p_to_apply.union_fixture_name))

                    # always use 'indirect' since that's a fixture.
                    calls = self._parametrize_calls(calls, p_to_apply.union_fixture_name,
                                                    p_to_apply.alternative_names, indirect=True,
                                                    ids=p_to_apply.ids,
                                                    scope=p_to_apply.scope, **p_to_apply.kwargs)

                    # now move to the children
                    nodes_children = [None] * len(calls)
                    for i in range(len(calls)):
                        active_alternative = calls[i].params[p_to_apply.union_fixture_name]
                        child_node = current_node.children[active_alternative.alternative_name]
                        child_pending = pending.copy()

                        # place the childs parameter in the first position if it is in the list
                        # not needed anymore - already automatic
                        # try:
                        #     child_pending.move_to_end(child_alternative, last=False)
                        # except KeyError:
                        #     # not in the list: the child alternative is a non-parametrized fixture
                        #     pass

                        calls[i], nodes_children[i] = self._process_node(child_node, child_pending, [calls[i]])

                    # finally flatten the list if needed
                    calls = flatten_list(calls)
                    nodes_children = flatten_list(nodes_children)
                    return calls, nodes_children


def _make_unique(lst):
    _set = set()

    def _first_time_met(v):
        if v not in _set:
            _set.add(v)
            return True
        else:
            return False

    return [v for v in lst if _first_time_met(v)]


def flatten_list(lst):
    return [v for nested_list in lst for v in nested_list]


def sort_according_to_ref_list(fixturenames, param_names):
    """
    Sorts items in the first list, according to their position in the second.
    Items that are not in the second list stay in the same position, the others are just swapped.
    A new list is returned.

    :param fixturenames:
    :param param_names:
    :return:
    """
    cur_indices = []
    for pname in param_names:
        try:
            cur_indices.append(fixturenames.index(pname))
        except (ValueError, IndexError):
            # can happen in case of indirect parametrization: a parameter is not in the fixture name.
            # TODO we should maybe rather add the pname to fixturenames in this case ?
            pass
    target_indices = sorted(cur_indices)
    sorted_fixturenames = list(fixturenames)
    for old_i, new_i in zip(cur_indices, target_indices):
        sorted_fixturenames[new_i] = fixturenames[old_i]
    return sorted_fixturenames


_OPTION_NAME = 'with_reorder'
_SKIP = 'skip'
_NORMAL = 'normal'
_OPTIONS = {
    _NORMAL: """(default) the usual reordering done by pytest to optimize setup/teardown of session- / module- 
/ class- fixtures, as well as all the modifications made by other plugins (e.g. pytest-reorder)""",
    _SKIP: """skips *all* reordering, even the one done by pytest itself or installed plugins 
(e.g. pytest-reorder)"""
}


# @hookspec(historic=True)
def pytest_addoption(parser):
    group = parser.getgroup('pytest-cases ordering', 'pytest-cases reordering options', after='general')
    help_str = """String specifying one of the reordering alternatives to use. Should be one of :
 - %s""" % ("\n - ".join(["%s: %s" % (k, v) for k, v in _OPTIONS.items()]))
    group.addoption(
        '--%s' % _OPTION_NAME.replace('_', '-'), type=str, default='normal', help=help_str
    )


# @hookspec(historic=True)
def pytest_configure(config):
    # validate the config
    allowed_values = ('normal', 'skip')
    reordering_choice = config.getoption(_OPTION_NAME)
    if reordering_choice not in allowed_values:
        raise ValueError("[pytest-cases] Wrong --%s option: %s. Allowed values: %s"
                         "" % (_OPTION_NAME, reordering_choice, allowed_values))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_collection_modifyitems(session, config, items):  # noqa
    """
    An alternative to the `reorder_items` function in fixtures.py
    (https://github.com/pytest-dev/pytest/blob/master/src/_pytest/fixtures.py#L209)

    We basically set back the previous order once the pytest ordering routine has completed.

    TODO we should set back an optimal ordering, but current PR https://github.com/pytest-dev/pytest/pull/3551
     will probably not be relevant to handle our "union" fixtures > need to integrate the NOT_USED markers in the method

    :param session:
    :param config:
    :param items:
    :return:
    """
    ordering_choice = config.getoption(_OPTION_NAME)

    if ordering_choice == _SKIP:
        # remember initial order
        initial_order = copy(items)
        yield
        # put back the initial order but keep the filter
        to_return = [None] * len(items)
        i = 0
        for item in initial_order:
            if item in items:
                to_return[i] = item
                i += 1
        assert i == len(items)
        items[:] = to_return

    else:
        # do nothing
        yield
