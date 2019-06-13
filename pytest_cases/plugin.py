from collections import OrderedDict, namedtuple
from distutils.version import LooseVersion
from functools import partial

from _pytest.fixtures import scopes as pt_scopes

import pytest

from pytest_cases.common import get_pytest_nodeid
from pytest_cases.main_fixtures import NOT_USED, is_fixture_union_params

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature


try:  # python 3.3+ type hints
    from typing import Optional, List, Tuple, Union, Iterable
    from _pytest.python import CallSpec2
except ImportError:
    pass


_DEBUG = True


# @hookspec(firstresult=True)
def pytest_collection(session):
    # override the fixture manager's method
    session._fixturemanager.getfixtureclosure = partial(getfixtureclosure, session._fixturemanager)


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
                'as_list', 'all_fixture_defs'

    def __init__(self, parent_node=None):
        self.parent = parent_node

        # these will be set after closure has been built
        self.fixture_defs = None
        self.split_fixture_name = None
        self.split_fixture_discarded_names = []
        self.children = OrderedDict()

        # this will be created after the first time the object is converted to a list (cache)
        self.as_list = None
        self.all_fixture_defs = None

    # ------

    def _to_str(self, indent_nb=0):

        indent = " " * indent_nb

        if not self.is_closure_built():
            str_repr = "<pending, incomplete>"
        else:
            str_repr = "%s(%s)  (discarded: %s)" \
                       "" % (indent,
                             ",".join([("%s" % f) for f in self.fixture_defs.keys()]),
                             self.split_fixture_discarded_names)

        if self.has_split():
            children_str_prefix = "\n%s - " % indent
            children_str = children_str_prefix + children_str_prefix.join([c._to_str(indent_nb=indent_nb+1)
                                                                           for c in self.children.values()])
            str_repr = str_repr + " split: " + self.split_fixture_name + children_str

        return str_repr

    def __repr__(self):
        return self._to_str()

    # ---- list facade

    def __iter__(self):
        return iter(self.to_list())

    def __getitem__(self, item):
        return self.to_list()[item]

    def to_list(self):
        """
        Converts self to a list to get all fixture names, and caches the result.
        The first time this is called, a non-none arg2fixturedefs object Must be provided to sort the fixture names
        according to scope.

        TODO maybe this sorting should actually be propagated down the tree so that it is done per branch

        :param arg2fixturedefs:
        :return:
        """
        if self.as_list is None:
            # crawl the tree to get the list of unique fixture names
            fixturenames_closure = self._to_list()

            if LooseVersion(pytest.__version__) >= LooseVersion('3.5.0'):
                # sort by scope
                def sort_by_scope(arg_name):
                    try:
                        fixturedefs = self.get_all_fixture_defs()[arg_name]
                    except KeyError:
                        return pt_scopes.index("function")
                    else:
                        return fixturedefs[-1].scopenum
                fixturenames_closure.sort(key=sort_by_scope)

            self.as_list = fixturenames_closure

        return self.as_list

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
        all = OrderedDict()
        for k, v in self.fixture_defs.items():
            if v is not None:
                all[k] = v
        for c in self.children.values():
            all.update(c.get_all_fixture_defs())
        return all

    # ---- utils to build the closure

    def build_closure(self,
                      fixture_defs_mgr,      # type: FixtureDefsCache
                      initial_fixture_names  # type: Iterable[str]
                      ):
        self._build_closure(fixture_defs_mgr, initial_fixture_names)

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
                       fixture_defs_mgr,      # type: FixtureDefsCache
                       initial_fixture_names  # type: Iterable[str]
                       ):
        """

        :param arg2fixturedefs: set of fixtures already known by the parent node
        :return: nothing (the input arg2fixturedefs is modified)
        """

        # Grab all dependencies of all fixtures present at this node and add them to either this or to nodes below.

        # -- first switch this object from 'pending' to 'under construction'
        self.fixture_defs = OrderedDict()

        # -- then for all pending, add them with their dependencies
        pending_fixture_names = list(initial_fixture_names)
        while len(pending_fixture_names) > 0:
            fixname = pending_fixture_names.pop(0)

            # if the fixture is already known in this node or above, do not care
            if self.already_knows_fixture(fixname):
                continue

            # else grab the fixture definition(s) for this fixture name for this test node id
            fixturedefs = fixture_defs_mgr.get_fixture_defs(fixname)
            if not fixturedefs:
                # fixture without definition: add it
                self.add_required_fixture(fixname, None)
            else:
                # the actual definition is the last one
                _fixdef = fixturedefs[-1]
                _params = _fixdef.params

                if _params is not None and is_fixture_union_params(_params):
                    # create an UNION fixture
                    if _fixdef.ids is not None:
                        raise ValueError("ids cannot be set on a union fixture")

                    # if there are direct dependencies that are not the union members, add them to pending
                    non_member_dependencies = [f for f in _fixdef.argnames if f not in _params]
                    pending_fixture_names += non_member_dependencies

                    # propagate WITH the pending
                    self.split_and_build(fixture_defs_mgr, fixname, fixturedefs, _params, pending_fixture_names)

                    # empty the pending
                    pending_fixture_names = []

                else:
                    # normal fixture
                    self.add_required_fixture(fixname, fixturedefs)

                    # add all dependencies in the to do list
                    dependencies = _fixdef.argnames
                    pending_fixture_names += dependencies

    # ------ tools to add new fixture names during closure construction

    def add_required_fixture(self, new_fixture_name, new_fixture_defs):
        """ Adds some required fixture names to this node. Returns True if new fixtures were added here (not in child)"""
        if self.already_knows_fixture(new_fixture_name):
            return
        elif not self.has_split():
            # add_required_fixture locally
            if new_fixture_name not in self.fixture_defs:
                self.fixture_defs[new_fixture_name] = new_fixture_defs
        else:
            raise ValueError("This should not happen anymore")
            # # add_required_fixture in each child
            # for c in self.children.values():
            #     c.add_required_fixture(new_fixture_name, new_fixture_defs)

    def split_and_build(self,
                        fixture_defs_mgr,           # type: FixtureDefsCache
                        split_fixture_name,         # type: str
                        split_fixture_defs,         # type: Tuple[FixtureDefinition]
                        alternative_fixture_names,  #
                        pending_fixtures_list       #
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
                new_c = FixtureClosureNode(self)
                self.children[f] = new_c

                # set the discarded fixture names
                new_c.split_fixture_discarded_names = [g for g in alternative_fixture_names if g != f]

                # perform the propagation:
                # create a copy of the pending fixtures list and prepend the fixture used
                pending_for_child = [f] + pending_fixtures_list
                new_c._build_closure(fixture_defs_mgr, pending_for_child)

    def has_split(self):
        return self.split_fixture_name is not None

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
    at_least_one_added = False
    for l in new_items:
        if l not in into_list:
            into_list.append(l)
            at_least_one_added = True
    return at_least_one_added


def getfixtureclosure(fm, fixturenames, parentnode):

    # first retrieve the normal pytest output for comparison
    outputs = fm.__class__.getfixtureclosure(fm, fixturenames, parentnode)
    if LooseVersion(pytest.__version__) >= LooseVersion('4.0.0'):
        initial_names, ref_fixturenames, ref_arg2fixturedefs = outputs
    else:
        ref_fixturenames, ref_arg2fixturedefs = outputs

    # now let's do it by ourselves.
    parentid = parentnode.nodeid

    # Create closure
    # -- auto-use fixtures
    _init_fixnames = fm._getautousenames(parentid)
    # -- required fixtures/params.
    merge(fixturenames, _init_fixnames)

    fixture_defs_mger = FixtureDefsCache(fm, parentid)
    fixturenames_closure_node = FixtureClosureNode()
    fixturenames_closure_node.build_closure(fixture_defs_mger, _init_fixnames)

    if _DEBUG:
        print("Closure for %s:" % parentid)
        print(fixturenames_closure_node)

    # sort the fixture names (note: only in recent pytest)
    fixturenames_closure_node.to_list()

    # FINALLY compare with the previous behaviour TODO remove when in 'production' ?
    assert fixturenames_closure_node.get_all_fixture_defs() == ref_arg2fixturedefs
    if fixturenames_closure_node.has_split():
        # order might be changed
        assert set((str(f) for f in fixturenames_closure_node)) == set(ref_fixturenames)
    else:
        # same order
        assert list(fixturenames_closure_node) == ref_fixturenames

    # and store our closure in the node
    # note as an alternative we could return a custom object in place of the ref_fixturenames
    # store_union_closure_in_node(fixturenames_closure_node, parentnode)

    # return ref_fixturenames, ref_arg2fixturedefs
    if LooseVersion(pytest.__version__) >= LooseVersion('4.0.0'):
        return initial_names, fixturenames_closure_node, ref_arg2fixturedefs
    else:
        return fixturenames_closure_node, ref_arg2fixturedefs


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


class UnionParamz(namedtuple('UnionParamz', ['union_fixture_name', 'alternative_names', 'scope', 'kwargs'])):
    """ Represents some parametrization to be applied, for a union fixture """

    __slots__ = ()

    def __str__(self):
        return "[UNION] %s=[%s], scope=%s, kwargs=%s" \
               "" % (self.union_fixture_name, ','.join([str(a) for a in self.alternative_names]),
                     self.scope, self.kwargs)


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
    if is_fixture_union_params(argvalues):
        if ',' in argnames or not isinstance(argnames, str):
            raise ValueError("Union fixtures can not be parametrized")
        union_fixture_name = argnames
        union_fixture_alternatives = argvalues
        if indirect is False or ids is not None or len(kwargs) > 0:
            raise ValueError("indirect or ids cannot be set on a union fixture")

        # add a union parametrization in the queue (but do not apply it now)
        calls_reactor.append(UnionParamz(union_fixture_name, union_fixture_alternatives, scope, kwargs))
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

        # transform it into a list of partitions (each contains a list of parameters to use)
        filters_list, fixtures_list, discarded_list = fix_closure_tree.get_alternatives()

        # ---- create all the `CallSpec2` instances
        # for each parameter to apply, apply it on all partitions if relevant
        calls_list = [None] * len(filters_list)

        def _parametrize_calls(init_calls, argnames, argvalues, discard_id, indirect=False, ids=None, scope=None,
                               **kwargs):
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
                    callspec._idlist.pop(-1)

            # restore the metafunc and return the new calls
            self.metafunc._calls = bak
            return new_calls

        def apply_parametrization(p_to_apply, i, pending):
            """ internal routine to apply a given parametrization on a range of partitions """

            # get additional info concerning that branch
            filters_dct, fixture_names = filters_list[i], fixtures_list[i]

            if isinstance(p_to_apply, UnionParamz):
                # (1) a "union" fixture: parametrize with the single value for that branch
                try:
                    # we will only parametrize with the "good" fixture value
                    selected_fixture_name = filters_dct[p_to_apply.union_fixture_name]
                    is_used = True
                except KeyError:
                    # this union is actually not used at this node. set to not used
                    selected_fixture_name = NOT_USED
                    is_used = False

                if _DEBUG:
                    print("[Branch %s: %s] Parametrizing with %s=%s"
                          "" % (i, filters_dct, p_to_apply.union_fixture_name, selected_fixture_name))

                # always use 'indirect' since that's a fixture.
                calls_list[i] = _parametrize_calls(calls_list[i], p_to_apply.union_fixture_name, [selected_fixture_name],
                                                   discard_id=(not is_used), indirect=True, scope=p_to_apply.scope,
                                                   **p_to_apply.kwargs)

                # now parametrize that alternative directly with the used fixture value if there is one
                if is_used:
                    try:
                        _paramz = pending.pop(selected_fixture_name)
                    except KeyError:
                        pass
                    else:
                        apply_parametrization(_paramz, i, pending)

            elif isinstance(p_to_apply, NormalParamz):
                # (B) a normal parameter / fixture
                # handle case where the name contains several names
                all_param_names = p_to_apply.argnames.replace(' ', '').split(',')

                # we only parametrize if that fixture/param is active on that branch, otherwise we set a dummy
                if len(all_param_names) > 1 or p_to_apply.argnames in fixture_names:
                    _vals = p_to_apply.argvalues
                    is_used = False
                else:
                    _vals = [NOT_USED]
                    is_used = True

                if _DEBUG:
                    print("[Branch %s: %s] Parametrizing with %s=%s" % (i, filters_dct, p_to_apply.argnames, _vals))

                calls_list[i] = _parametrize_calls(calls_list[i], p_to_apply.argnames, _vals,
                                                   indirect=p_to_apply.indirect, ids=p_to_apply.ids,
                                                   discard_id=is_used, scope=p_to_apply.scope, **p_to_apply.kwargs)

            else:
                raise TypeError("Invalid parametrization type: %s" % p_to_apply.__class__)

        # Apply all parametrizations for all alternative branches
        for i in range(len(calls_list)):
            # copy the list of pending parametrization in a dictionary
            pending = OrderedDict([(str(p[0]), p) for p in self._pending])

            # apply all of them
            while len(pending) > 0:
                p_name, p_to_apply = pending.popitem(last=False)
                apply_parametrization(p_to_apply, i, pending)

        if _DEBUG:
            print("\n".join(["%s[%s]: funcargs=%s, params=%s" % (get_pytest_nodeid(self.metafunc),
                                                                 c.id, c.funcargs, c.params)
                             for calls in calls_list for c in calls]))
            print()

        # cleanup:
        # some non-parametrized fixtures may need to be explicitly deactivated in some callspecs
        # otherwise they will be setup/teardown.
        #
        # For this we use a dirty hack: we add a parameter with they name in the callspec, it seems to be propagated
        # in the `request`. TODO is there a better way
        for calls, filters_dct, fix_names, discarded_fix_names \
                in zip(calls_list, filters_list, fixtures_list, discarded_list):
            for c in calls:
                for df in discarded_fix_names:
                    fixture_to_discard = str(df)
                    if fixture_to_discard not in c.params:
                        # explicitly add it as discarded by creating a parameter value for it.
                        c.params[fixture_to_discard] = NOT_USED

        # finalize the parametrization by flattening the list
        self._call_list = [c for calls in calls_list for c in calls]

        # put back self as the _calls facade
        self.metafunc._calls = bak_calls

        # forget about all parametrizations now - this wont happen again
        self._pending = None


def _make_unique(lst):
    _set = set()

    def _first_time_met(v):
        if v not in _set:
            _set.add(v)
            return True
        else:
            return False

    return [v for v in lst if _first_time_met(v)]

