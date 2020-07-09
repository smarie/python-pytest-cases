from distutils.version import LooseVersion
from functools import partial

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature  # noqa

try:
    from typing import Union, Callable, List, Any, Sequence, Optional  # noqa
except ImportError:
    pass

import pytest

from .common_pytest_marks import get_pytest_marks_on_function, transform_marks_into_decorators


pytest53 = LooseVersion(pytest.__version__) >= LooseVersion("5.3.0")
if pytest53:
    # in the latest versions of pytest, the default _idmaker returns the value of __name__ if it is available,
    # even if an object is not a class nor a function. So we do not need to use any special trick.
    _LazyValueBase = object
else:
    fake_base = int

    class _LazyValueBase(int, object):
        """
        in this older version of pytest, the default _idmaker does *not* return the value of __name__ for
        objects that are not functions not classes. However it *does* return str(obj) for objects that are
        instances of bool, int or float. So that's why lazy_value inherits from int.
        """
        __slots__ = ()

        def __new__(cls, *args, **kwargs):
            """ Inheriting from int is a bit hard in python: we have to override __new__ """
            obj = fake_base.__new__(cls, 111111)  # noqa
            cls.__init__(obj, *args, **kwargs)  # noqa
            return obj

        def __getattribute__(self, item):
            """Map all default attribute and method access to the ones in object, not in int"""
            return object.__getattribute__(self, item)

        def __repr__(self):
            """Magic methods are not intercepted by __getattribute__ and need to be overridden manually.
            We do not need all of them by at least override this one for easier debugging"""
            return object.__repr__(self)


class Lazy(object):
    """
    All lazy items should inherit from this for good pytest compliance (ids, marks, etc.)
    """
    # @abstractmethod
    def get_id(self):
        """Return the id to use by pytest"""
        raise NotImplementedError()

    # @abstractmethod
    def get(self):
        """Return the value to use by pytest"""
        raise NotImplementedError()

    def __str__(self):
        """in pytest<5.3 we inherit from int so that str(v) is called by pytest _idmaker to get the id

        In later pytest this is extremely convenient to have this string representation
        for example to use in pytest-harvest results tables, so we still keep it.
        """
        return self.get_id()

    @property
    def __name__(self):
        """for pytest >= 5.3 we override this so that pytest uses it for id"""
        return self.get_id()


def _unwrap(obj):
    """A light copy of _pytest.compat.get_real_func. In our case
    we do not wish to unwrap the partial nor handle pytest fixture
    Note: maybe from inspect import unwrap could do the same?
    """
    start_obj = obj
    for i in range(100):
        # __pytest_wrapped__ is set by @pytest.fixture when wrapping the fixture function
        # to trigger a warning if it gets called directly instead of by pytest: we don't
        # want to unwrap further than this otherwise we lose useful wrappings like @mock.patch (#3774)
        # new_obj = getattr(obj, "__pytest_wrapped__", None)
        # if isinstance(new_obj, _PytestWrapper):
        #     obj = new_obj.obj
        #     break
        new_obj = getattr(obj, "__wrapped__", None)
        if new_obj is None:
            break
        obj = new_obj
    else:
        raise ValueError("could not find real function of {start}\nstopped at {current}".format(
                start=repr(start_obj), current=repr(obj)
            )
        )
    return obj


def partial_to_str(partialfun):
    """Return a string representation of a partial function, to use in lazy_value ids"""
    strwds = ", ".join("%s=%s" % (k, v) for k, v in partialfun.keywords.items())
    if len(partialfun.args) > 0:
        strargs = ', '.join(str(i) for i in partialfun.args)
        if len(partialfun.keywords) > 0:
            strargs = "%s, %s" % (strargs, strwds)
    else:
        strargs = strwds
    return "%s(%s)" % (partialfun.func.__name__, strargs)


# noinspection PyPep8Naming
class LazyValue(Lazy, _LazyValueBase):
    """
    A reference to a value getter, to be used in `parametrize_plus`.

    A `lazy_value` is the same thing than a function-scoped fixture, except that the value getter function is not a
    fixture and therefore can neither be parametrized nor depend on fixtures. It should have no mandatory argument.
    """
    if pytest53:
        __slots__ = 'valuegetter', '_id', '_marks'
    else:
        # we can not define __slots__ since we extend int,
        # see https://docs.python.org/3/reference/datamodel.html?highlight=__slots__#notes-on-using-slots
        pass

    # noinspection PyMissingConstructor
    def __init__(self,
                 valuegetter,  # type: Callable[[], Any]
                 id=None,      # type: str  # noqa
                 marks=()      # type: Union[Any, Sequence[Any]]
                 ):
        self.valuegetter = valuegetter
        self._id = id
        if isinstance(marks, (tuple, list, set)):
            self._marks = marks
        else:
            self._marks = (marks, )

    def get_marks(self, as_decorators=False):
        """
        Overrides default implementation to return the marks that are on the case function

        :param as_decorators: when True, the marks will be transformed into MarkDecorators before being
            returned
        :return:
        """
        valuegetter_marks = get_pytest_marks_on_function(self.valuegetter, as_decorators=as_decorators)

        if self._marks:
            return transform_marks_into_decorators(self._marks) + valuegetter_marks
        else:
            return valuegetter_marks

    def get_id(self):
        """The id to use in pytest"""
        if self._id is not None:
            return self._id
        else:
            # default is the __name__ of the value getter
            _id = getattr(self.valuegetter, '__name__', None)
            if _id is not None:
                return _id

            # unwrap and handle partial functions
            vg = _unwrap(self.valuegetter)

            if isinstance(vg, partial):
                return partial_to_str(vg)
            else:
                return vg.__name__

    def get(self):
        return self.valuegetter()

    def as_lazy_tuple(self, nb_params):
        return LazyTuple(self, nb_params)

    def as_lazy_items_list(self, nb_params):
        return [v for v in LazyTuple(self, nb_params)]


class LazyTupleItem(Lazy, _LazyValueBase):
    """
    An item in a Lazy Tuple
    """
    if pytest53:
        __slots__ = 'host', 'item'
    else:
        # we can not define __slots__ since we extend int,
        # see https://docs.python.org/3/reference/datamodel.html?highlight=__slots__#notes-on-using-slots
        pass

    # noinspection PyMissingConstructor
    def __init__(self,
                 host,  # type: LazyTuple
                 item   # type: int
                 ):
        self.host = host
        self.item = item

    def get_id(self):
        return "%s[%s]" % (self.host.get_id(), self.item)

    def get(self):
        return self.host.force_getitem(self.item)


class LazyTuple(Lazy):
    """
    A wrapper representing a lazy_value used as a tuple = for several argvalues at once.

     -
       while not calling the lazy value
     -
    """
    __slots__ = ('value', 'theoretical_size', 'retrieved')

    # noinspection PyMissingConstructor
    def __init__(self,
                 valueref,         # type: Union[LazyValue, Sequence]
                 theoretical_size  # type: int
                 ):
        self.value = valueref
        self.theoretical_size = theoretical_size
        self.retrieved = False

    def __len__(self):
        return self.theoretical_size

    def get_id(self):
        """return the id to use by pytest"""
        return self.value.get_id()

    def get(self):
        """ Call the underlying value getter, then return the tuple (not self) """
        if not self.retrieved:
            # retrieve
            self.value = self.value.get()
            self.retrieved = True
        return self.value

    def __getitem__(self, item):
        """
        Getting an item in the tuple with self[i] does *not* retrieve the value automatically, but returns
        a facade (a LazyTupleItem), so that pytest can store this item independently wherever needed, without
        yet calling the value getter.
        """
        if self.retrieved:
            # this is never called by pytest, but keep it for debugging
            return self.value[item]
        elif item >= self.theoretical_size:
            raise IndexError(item)
        else:
            # do not retrieve yet: return a facade
            return LazyTupleItem(self, item)

    def force_getitem(self, item):
        """ Call the underlying value getter, then return self[i]. """
        getter = self.value
        argvalue = self.get()
        try:
            return argvalue[item]
        except TypeError as e:
            raise ValueError("(lazy_value) The parameter value returned by `%r` is not compliant with the number"
                             " of argnames in parametrization (%s). A %s-tuple-like was expected. "
                             "Returned lazy argvalue is %r and argvalue[%s] raised %s: %s"
                             % (getter.valuegetter, self.theoretical_size, self.theoretical_size,
                                argvalue, item, e.__class__, e))


def lazy_value(valuegetter,  # type: Callable[[], Any]
               id=None,      # type: str  # noqa
               marks=()      # type: Union[Any, Sequence[Any]]
               ):
    """
    Creates a reference to a value getter, to be used in `parametrize_plus`.

    A `lazy_value` is the same thing than a function-scoped fixture, except that the value getter function is not a
    fixture and therefore can neither be parametrized nor depend on fixtures. It should have no mandatory argument.

    Note that a `lazy_value` can be included in a `pytest.param` without problem. In that case the id defined by
    `pytest.param` will take precedence over the one defined in `lazy_value` if any. The marks, however,
    will all be kept wherever they are defined.

    :param valuegetter: a callable without mandatory arguments
    :param id: an optional id. Otherwise `valuegetter.__name__` will be used by default
    :param marks: optional marks. `valuegetter` marks will also be preserved.
    """
    return LazyValue(valuegetter, id=id, marks=marks)


def is_lazy_value(argval):
    try:
        return isinstance(argval, LazyValue)
    except:
        return False


def is_lazy(argval):
    try:
        return isinstance(argval, (LazyValue, LazyTuple, LazyTupleItem))
    except:
        return False


def get_lazy_args(argval):
    """ Possibly calls the lazy values contained in argval if needed, before returning it"""

    try:
        _is_lazy = is_lazy(argval)
    except:  # noqa
        return argval
    else:
        if _is_lazy:
            return argval.get()
        else:
            return argval
