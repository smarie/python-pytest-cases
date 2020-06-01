from __future__ import division

from inspect import getmodule, currentframe
from warnings import warn

try:
    # type hints, python 3+
    from typing import Callable, Any, Union, Iterable  # noqa
    from types import ModuleType  # noqa
except ImportError:
    pass


class ExistingFixtureNameError(ValueError):
    """
    Raised by `add_fixture_to_callers_module` when a fixture already exists in a module
    """
    def __init__(self, module, name, caller):
        self.module = module
        self.name = name
        self.caller = caller

    def __str__(self):
        return "Symbol `%s` already exists in module %s and therefore a corresponding fixture can not be created by " \
               "`%s`" % (self.name, self.module, self.caller)


RAISE = 0
WARN = 1
CHANGE = 2


def check_name_available(module,
                         name,                  # type: str
                         if_name_exists=RAISE,  # type: int
                         caller=None,           # type: Callable[[Any], Any]
                         ):
    """
    Routine to

    :param module:
    :param name:
    :param if_name_exists:
    :param caller:
    :return: a name that might be different if policy was CHANGE
    """
    if name in dir(module):
        if caller is None:
            caller = ''

        # Name already exists: act according to policy
        if if_name_exists is RAISE:
            raise ExistingFixtureNameError(module, name, caller)

        elif if_name_exists is WARN:
            warn("%s Overriding symbol %s in module %s" % (caller, name, module))

        elif if_name_exists is CHANGE:
            # find a non-used name in that module
            i = 1
            name2 = name + '_%s' % i
            while name2 in dir(module):
                i += 1
                name2 = name + '_%s' % i
            name = name2
        else:
            raise ValueError("invalid value for `if_name_exists`: %s" % if_name_exists)

    return name


def get_caller_module(frame_offset=1):
    # type: (...) -> ModuleType
    """ Return the module where the last frame belongs.

    :param frame_offset: an alternate offset to look further up in the call stack
    :return:
    """
    # grab context from the caller frame
    frame = _get_callerframe(offset=frame_offset)
    return getmodule(frame)


def _get_callerframe(offset=0):
    """ Return a frame in the call stack

    :param offset: an alternate offset to look further up in the call stack
    :return:
    """
    # inspect.stack is extremely slow, the fastest is sys._getframe or inspect.currentframe().
    # See https://gist.github.com/JettJones/c236494013f22723c1822126df944b12
    # frame = sys._getframe(2 + offset)
    frame = currentframe()
    for _ in range(2 + offset):
        frame = frame.f_back
    return frame
