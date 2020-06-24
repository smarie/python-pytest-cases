# Use true division operator always even in old python 2.x (used in `_extract_cases_from_module`)
from __future__ import division

from functools import partial
from importlib import import_module
from inspect import getmembers
from warnings import warn

from pytest_cases import parametrize_plus, lazy_value

try:
    from typing import Union, Callable, Iterable, Any, Type, List  # noqa
except ImportError:
    pass

from .common_mini_six import string_types
from .common_pytest import get_code, safe_isclass

from .case_funcs_new import matches_tag_query, is_case_function, CASE_FIELD, CaseInfo, is_case_class

AUTO = object()
"""Marker that can be used instead of a module name to indicate that the module is the one named `test_*_cases.py`"""

AUTO2 = object()
"""Marker that can be used instead of a module name to indicate that the module is the one named `cases_*.py`"""

THIS_MODULE = object()
"""Singleton that can be used instead of a module name to indicate that the module is the current one"""

try:
    from typing import Literal  # noqa
    from types import ModuleType  # noqa
    ModuleRef = Union[str, ModuleType, Literal[THIS_MODULE]]  # noqa
    CasesHolder = Union[ModuleRef, Type]
except ImportError:
    pass


def parametrize_with_cases(argnames,    # type : str
                           cases=AUTO,  # type: Union[Callable, CasesHolder, Iterable[Callable], Iterable[CasesHolder]]
                           **kwargs
                           ):
    # type: (...) -> Callable[[Callable], Callable]
    """
    A decorator for test functions, to parametrize them based on test cases.

    By default the list of test cases is automatically drawn from the file named `<name>_cases.py` where `<name>` is
    the current module name.
    This list can otherwise either be provided explicitly in the `cases` argument, or referenced
    as a python module or a list of python modules in the `cases` argument.

    :param argnames: same than in @pytest.mark.parametrize
    :param cases: a single case or a hardcoded list of cases ; or a container (module or class) or hardcoded list of
        containers. You may use `THIS_MODULE` to include current module. `AUTO` means that the module named
        `<name>_cases.py` will be loaded, where `<name>.py` is the module file of the decorated function.
    :return:
    """
    # Handle single elements
    try:
        cases = tuple(cases)
    except TypeError:
        cases = (cases,)

    def _apply_parametrization(f):
        """

        :param f:
        :return:
        """
        caller_module = '.'.join(f.__module__.split('.')[:-1])

        cases_funs = []
        for c in cases:
            # load case or cases depending on type
            if safe_isclass(c):
                # class
                new_cases = extract_cases_from_class(c, has_tag=None, filter=None)
                cases_funs += new_cases
            elif callable(c):
                # function
                if is_case_function(c, enforce_prefix=False):
                    cases_funs.append(c)
                else:
                    raise ValueError("Unsupported case function: %r" % c)
            else:
                # module
                if c is AUTO:
                    c = import_default_cases_module(f)
                elif c is AUTO2:
                    c = import_default_cases_module(f, alt_name=True)
                elif c is THIS_MODULE:
                    c = f.__module__
                new_cases = extract_cases_from_module(c, has_tag=None, filter=None, caller_module=caller_module)
                cases_funs += new_cases

        # Transform the various functions found
        argvalues = [case_to_argvalue(_f) for _f in cases_funs]

        # Finally apply parametrization
        _parametrize_with_cases = parametrize_plus(argnames, argvalues, **kwargs)
        return _parametrize_with_cases(f)

    return _apply_parametrization


def case_to_argvalue(f):
    """
    If f is a cases generator (a parametrized case) and/or if it has at least one argument,
    transform it into a fixture and return a fixture ref.

     - find if there are any unparametrized arguments (like pytest)
     - if none, this can be expanded in a lazy_value()

    :param f:
    :return:
    """
    id = None
    marks = ()

    case_info = getattr(f, CASE_FIELD, None)  # type: CaseInfo
    if case_info is not None:
        id = case_info.id
        marks = case_info.marks

    if id is None:
        # default test id from function name
        if f.__name__.startswith('case_'):
            id = f.__name__[5:]
        elif f.__name__.startswith('cases_'):
            id = f.__name__[6:]
        else:
            id = f.__name__

    return lazy_value(f, id=id, marks=marks)


def import_default_cases_module(f, alt_name=False):
    """
    Implements the `module=AUTO` behaviour of `@parameterize_cases`: based on the decorated test function `f`,
    it finds its containing module name "<test_module>.py" and then tries to import the python module
    "<test_module>_cases.py".

    Alternately if `alt_name=True` the name pattern to use will be `cases_<module>.py` when the test module is named
    `test_<module>.py`.

    :param f: the decorated test function
    :param alt_name: a boolean (default False) to use the alternate naming scheme.
    :return:
    """
    if alt_name:
        parts = f.__module__.split('.')
        assert parts[-1][0:5] == 'test_'
        cases_module_name = "%s.cases_%s" % ('.'.join(parts[:-1]), parts[-1][5:])
    else:
        cases_module_name = "%s_cases" % f.__module__

    try:
        cases_module = import_module(cases_module_name)
    except ImportError:
        raise ValueError("Could not import test cases module with module=AUTO pattern: unable to import %r"
                         % cases_module_name)
    return cases_module


def hasinit(obj):
    init = getattr(obj, "__init__", None)
    if init:
        return init != object.__init__


def hasnew(obj):
    new = getattr(obj, "__new__", None)
    if new:
        return new != object.__new__


class CasesCollectionWarning(UserWarning):
    """
    Warning emitted when pytest cases is not able to collect a file or symbol in a module.
    """
    __module__ = "pytest_cases"


def extract_cases_from_class(cls,
                             has_tag=None,  # type: Any
                             filter=None,   # type: Callable[[Iterable[Any]], bool]  # noqa
                             _case_param_factory=None
                             ):
    # type: (...) -> List[Callable]
    """

    :param cls:
    :param has_tag:
    :param filter:
    :return:
    """
    if is_case_class(cls):
        # see
        from _pytest.python import pytest_pycollect_makeitem

        if hasinit(cls):
            warn(
                CasesCollectionWarning(
                    "cannot collect cases class %r because it has a "
                    "__init__ constructor"
                    % (cls.__name__, )
                )
            )
            return []
        elif hasnew(cls):
            warn(
                CasesCollectionWarning(
                    "cannot collect test class %r because it has a "
                    "__new__ constructor"
                    % (cls.__name__, )
                )
            )
            return []

        return _extract_cases_from_module_or_class(cls=cls, has_tag=has_tag, filter=filter,
                                                   _case_param_factory=_case_param_factory)
    else:
        return []


def extract_cases_from_module(module,        # type: ModuleRef
                              has_tag=None,  # type: Any
                              filter=None,   # type: Callable[[Iterable[Any]], bool]  # noqa
                              caller_module=None,  # type: str
                              _case_param_factory=None
                              ):
    # type: (...) -> List[Callable]
    """
    Internal method used to create a list of `CaseDataGetter` for all cases available from the given module.
    See `@cases_data`

    See also `_pytest.python.PyCollector.collect` and `_pytest.python.PyCollector._makeitem` and
    `_pytest.python.pytest_pycollect_makeitem`: we could probably do this in a better way in pytest_pycollect_makeitem

    :param module:
    :param has_tag: a tag used to filter the cases. Only cases with the given tag will be selected
    :param filter: a function taking as an input a list of tags associated with a case, and returning a boolean
        indicating if the case should be selected
    :return:
    """
    # optionally import module if passed as module name string
    if isinstance(module, string_types):
        module = import_module(module, package=caller_module)

    return _extract_cases_from_module_or_class(module=module, has_tag=has_tag, filter=filter,
                                               _case_param_factory=_case_param_factory)


def _extract_cases_from_module_or_class(module=None,   # type: ModuleRef
                                        cls=None,      # type: Type
                                        has_tag=None,  # type: Any
                                        filter=None,   # type: Callable[[Iterable[Any]], bool]  # noqa
                                        _case_param_factory=None
                                        ):
    """

    :param module:
    :param has_tag:
    :param filter:
    :param _case_param_factory:
    :return:
    """
    if not ((cls is None) ^ (module is None)):
        raise ValueError("Only one of cls or module should be provided")

    container = cls or module

    if filter is not None and not callable(filter):
        raise ValueError("`filter` should be a callable starting in pytest-cases 0.8.0. If you wish to provide a single"
                         " tag to match, use `has_tag` instead.")

    # We will gather all cases in the reference module and put them in this dict (line no, case)
    cases_dct = dict()

    # List members - only keep the functions from the module file (not the imported ones)
    if module is not None:
        def _of_interest(f):
            # check if the function is actually *defined* in this module (not imported from elsewhere)
            # Note: we used code.co_filename == module.__file__ in the past
            # but on some targets the file changes to a cached one so this does not work reliably,
            # see https://github.com/smarie/python-pytest-cases/issues/72
            try:
                return f.__module__ == module.__name__
            except:  # noqa
                return False
    else:
        _of_interest = lambda x: True

    for m_name, m in getmembers(container, _of_interest):
        if is_case_class(m):
            cls_cases = extract_cases_from_class(m, has_tag=has_tag, filter=filter,
                                                 _case_param_factory=_case_param_factory)
            for _i, _m_item in enumerate(cls_cases):
                gen_line_nb = code.co_firstlineno + (_i / len(cls_cases))
                cases_dct[gen_line_nb] = _m_item

        elif is_case_function(m):
            code = get_code(m)
            if cls is not None:
                if isinstance(cls.__dict__[m_name], (staticmethod, classmethod)):
                    # skip it
                    continue
                # unwrap the function to get one without the 'self' argument
                _name = m.__name__
                m = partial(m, cls())
                m.__name__ = _name

            if matches_tag_query(m, has_tag=has_tag, filter=filter):
                if _case_param_factory is None:
                    # Nominal usage: put the case in the dictionary
                    cases_dct[code.co_firstlineno] = m
                else:
                    # Legacy usage where the cases generators were expanded here and inserted with a virtual line no
                    _case_param_factory(m, code, cases_dct)

    # convert into a list, taking all cases in order of appearance in the code (sort by source code line number)
    cases = [cases_dct[k] for k in sorted(cases_dct.keys())]

    return cases


# Below is the beginning of a switch from our code scanning tool above to the same one than pytest.
# from .common_pytest import is_fixture, safe_isclass, compat_get_real_func, compat_getfslineno
#
#
# class PytestCasesWarning(UserWarning):
#     """
#     Bases: :class:`UserWarning`.
#
#     Base class for all warnings emitted by pytest cases.
#     """
#
#     __module__ = "pytest_cases"
#
#
# class PytestCasesCollectionWarning(PytestCasesWarning):
#     """
#     Bases: :class:`PytestCasesWarning`.
#
#     Warning emitted when pytest cases is not able to collect a file or symbol in a module.
#     """
#
#     __module__ = "pytest_cases"
#
#
# class CasesModule(object):
#     """
#     A collector for test cases
#     This is a very lightweight version of `_pytest.python.Module`, the pytest collector for test functions and classes.
#
#     See also pytest_collect_file and pytest_pycollect_makemodule hooks
#     """
#     __slots__ = 'obj'
#
#     def __init__(self, module):
#         self.obj = module
#
#     def collect(self):
#         """
#         A copy of pytest Module.collect (PyCollector.collect actually)
#         :return:
#         """
#         if not getattr(self.obj, "__test__", True):
#             return []
#
#         # NB. we avoid random getattrs and peek in the __dict__ instead
#         # (XXX originally introduced from a PyPy need, still true?)
#         dicts = [getattr(self.obj, "__dict__", {})]
#         for basecls in getmro(self.obj.__class__):
#             dicts.append(basecls.__dict__)
#         seen = {}
#         values = []
#         for dic in dicts:
#             for name, obj in list(dic.items()):
#                 if name in seen:
#                     continue
#                 seen[name] = True
#                 res = self._makeitem(name, obj)
#                 if res is None:
#                     continue
#                 if not isinstance(res, list):
#                     res = [res]
#                 values.extend(res)
#
#         def sort_key(item):
#             fspath, lineno, _ = item.reportinfo()
#             return (str(fspath), lineno)
#
#         values.sort(key=sort_key)
#         return values
#
#     def _makeitem(self, name, obj):
#         """ An adapted copy of _pytest.python.pytest_pycollect_makeitem """
#         if safe_isclass(obj):
#             if self.iscaseclass(obj, name):
#                 raise ValueError("Case classes are not yet supported: %r" % obj)
#         elif self.iscasefunction(obj, name):
#             # mock seems to store unbound methods (issue473), normalize it
#             obj = getattr(obj, "__func__", obj)
#             # We need to try and unwrap the function if it's a functools.partial
#             # or a functools.wrapped.
#             # We mustn't if it's been wrapped with mock.patch (python 2 only)
#             if not (isfunction(obj) or isfunction(compat_get_real_func(obj))):
#                 filename, lineno = compat_getfslineno(obj)
#                 warn_explicit(
#                     message=PytestCasesCollectionWarning(
#                         "cannot collect %r because it is not a function." % name
#                     ),
#                     category=None,
#                     filename=str(filename),
#                     lineno=lineno + 1,
#                 )
#             elif getattr(obj, "__test__", True):
#                 if isgeneratorfunction(obj):
#                     filename, lineno = compat_getfslineno(obj)
#                     warn_explicit(
#                         message=PytestCasesCollectionWarning(
#                             "cannot collect %r because it is a generator function." % name
#                         ),
#                         category=None,
#                         filename=str(filename),
#                         lineno=lineno + 1,
#                     )
#                 else:
#                     res = list(self._gencases(name, obj))
#                 outcome.force_result(res)
#
#     def iscasefunction(self, obj, name):
#         """Similar to PyCollector.istestfunction"""
#         if name.startswith("case_"):
#             if isinstance(obj, staticmethod):
#                 # static methods need to be unwrapped
#                 obj = getattr(obj, "__func__", False)
#             return (
#                 getattr(obj, "__call__", False)
#                 and not is_fixture(obj) is None
#             )
#         else:
#             return False
#
#     def iscaseclass(self, obj, name):
#         """Similar to PyCollector.istestclass"""
#         return name.startswith("Case")
#
#     def _gencases(self, name, funcobj):
#         # generate the case associated with a case function object.
#         # note: the original PyCollector._genfunctions has a "metafunc" mechanism here, we do not need it.
#         return []
#
#
