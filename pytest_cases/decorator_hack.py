import sys

from itertools import chain

from decorator import FunctionMaker
from inspect import isgeneratorfunction

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature

try:
    from decorator import iscoroutinefunction
except ImportError:
    try:
        from inspect import iscoroutinefunction
    except ImportError:
        # let's assume there are no coroutine functions in old Python
        def iscoroutinefunction(f):
            return False


class MyFunctionMaker(FunctionMaker):
    """
    Overrides FunctionMaker so that additional arguments can be inserted in the resulting signature.
    """

    def refresh_signature(self):
        """Update self.signature and self.shortsignature based on self.args,
        self.varargs, self.varkw"""
        allargs = list(self.args)
        allshortargs = list(self.args)
        if self.varargs:
            allargs.append('*' + self.varargs)
            allshortargs.append('*' + self.varargs)
        elif self.kwonlyargs:
            allargs.append('*')  # single star syntax
        for a in self.kwonlyargs:
            allargs.append('%s=None' % a)
            allshortargs.append('%s=%s' % (a, a))
        if self.varkw:
            allargs.append('**' + self.varkw)
            allshortargs.append('**' + self.varkw)
        self.signature = ', '.join(allargs)
        self.shortsignature = ', '.join(allshortargs)

    @classmethod
    def create(cls, obj, body, evaldict, defaults=None,
               doc=None, module=None, addsource=True, add_args=(), del_args=(), **attrs):
        """
        Create a function from the strings name, signature and body.
        evaldict is the evaluation dictionary. If addsource is true an
        attribute __source__ is added to the result. The attributes attrs
        are added, if any.

        If add_args is not empty, these arguments will be prepended to the
        positional arguments.

        If del_args is not empty, these arguments will be removed from signature
        """
        if isinstance(obj, str):  # "name(signature)"
            name, rest = obj.strip().split('(', 1)
            signature = rest[:-1]  # strip a right parens
            func = None
        else:  # a function
            name = None
            signature = None
            func = obj
        self = cls(func, name, signature, defaults, doc, module)
        ibody = '\n'.join('    ' + line for line in body.splitlines())
        caller = evaldict.get('_call_')  # when called from `decorate`
        if caller and iscoroutinefunction(caller):
            body = ('async def %(name)s(%(signature)s):\n' + ibody).replace(
                'return', 'return await')
        else:
            body = 'def %(name)s(%(signature)s):\n' + ibody

            # Handle possible signature changes
            sig_modded = False
            if len(add_args) > 0:
                # prepend them as positional args - hence the reversed()
                for arg in reversed(add_args):
                    if arg not in self.args:
                        self.args = [arg] + self.args
                        sig_modded = True
                    else:
                        # the argument already exists in the wrapped
                        # function, nothing to do.
                        pass

            if len(del_args) > 0:
                # remove the args
                for to_remove in del_args:
                    for where_field in ('args', 'varargs', 'varkw', 'defaults', 'kwonlyargs', 'kwonlydefaults'):
                        a = getattr(self, where_field, None)
                        if a is not None and to_remove in a:
                            try:
                                # list
                                a.remove(to_remove)
                            except AttributeError:
                                # dict-like
                                del a[to_remove]
                            finally:
                                sig_modded = True

            if sig_modded:
                self.refresh_signature()

            # make the function
            func = self.make(body, evaldict, addsource, **attrs)

            if sig_modded:
                # delete this annotation otherwise inspect.signature
                # will wrongly return the signature of func.__wrapped__
                # instead of the signature of func
                func.__wrapped_with_addargs__ = func.__wrapped__
                del func.__wrapped__

            return func


def _extract_additional_args(f_sig, add_args_names, args, kwargs, put_all_in_kwargs=False):
    """
    Processes the arguments received by our caller so that at the end, args
    and kwargs only contain what is needed by f (according to f_sig). All
    additional arguments are returned separately, in order described by
    `add_args_names`. If some names in `add_args_names` are present in `f_sig`,
    then the arguments will appear both in the additional arguments and in
    *args, **kwargs.

    In the end, only *args can possibly be modified by the procedure (by removing
    from it all additional arguments that were not in f_sig and were prepended).

    So the result is a tuple (add_args, args)

    :return: a tuple (add_args, args) where `add_args` are the values of
        arguments named in `add_args_names` in the same order ; and `args` is
        the positional arguments to send to the wrapped function together with
        kwargs (args now only contains the positional args that are required by
        f, without the extra ones)
    """
    # -- first extract (and remove) the 'truly' additional ones (the ones not in the signature)
    add_args = [None] * len(add_args_names)
    for i, arg_name in enumerate(add_args_names):
        if arg_name not in f_sig.parameters:
            # remove this argument from the args and put it in the right place
            add_args[i] = args[0]
            args = args[1:]

    # -- then copy the ones that already exist in the signature. Thanks,inspect pkg!
    bound = f_sig.bind(*args, **kwargs)
    for i, arg_name in enumerate(add_args_names):
        if arg_name in f_sig.parameters:
            add_args[i] = bound.arguments[arg_name]

    # -- finally move args to kwargs of needed
    if put_all_in_kwargs:
        args = tuple()
        kwargs = {arg_name: bound.arguments[arg_name] for arg_name in f_sig.parameters}

    return add_args, args, kwargs


def _wrap_caller_for_additional_args(func, caller, additional_args, removed_args):
    """
    This internal function wraps the caller so as to handle all cases
    (if some additional args are already present in the signature or not)
    so as to ensure a consistent caller signature.

    Note: as of today if removed_args is not empty, positional args can not be correctly handled so all arguments
    are passed as kwargs to the wrapper

    :return: a new caller wrapping the caller, to be used in `decorate`
    """
    f_sig = signature(func)

    # We will create a caller above the original caller in order to check
    # if additional_args are already present in the signature or not, and
    # act accordingly
    original_caller = caller

    # If we have to remove the parameters, the behaviour and signatures will be a bit different
    # First modify the signature so that we remove the parameters that have to be.
    if len(removed_args) > 0:
        # new_params = OrderedDict(((k, v) for k, v in f_sig.parameters.items() if k not in removed_args))
        new_params = (v for k, v in f_sig.parameters.items() if k not in removed_args)
        f_sig = f_sig.replace(parameters=new_params)

    # -- then create the appropriate function signature according to
    # wrapped function signature assume that original_caller has all
    # additional args as first positional arguments, in order
    if not isgeneratorfunction(original_caller):
        def caller(f, *args, **kwargs):
            # Retrieve the values for additional args.
            add_args, args, kwargs = _extract_additional_args(f_sig, additional_args,
                                                              args, kwargs,
                                                              put_all_in_kwargs=(len(removed_args) > 0))

            # Call the original caller
            # IMPORTANT : args and kwargs are passed without the double-star here!
            return original_caller(f, *add_args, args=args, kwargs=kwargs)
    else:
        def caller(f, *args, **kwargs):
            # Retrieve the value for additional args.
            add_args, args, kwargs = _extract_additional_args(f_sig, additional_args,
                                                              args, kwargs,
                                                              put_all_in_kwargs=(len(removed_args) > 0))

            # Call the original caller
            # IMPORTANT : args and kwargs are passed without the double-star here!
            for res in original_caller(f, *add_args, args=args, kwargs=kwargs):
                yield res

    return caller


def my_decorate(func, caller, extras=(), additional_args=(), removed_args=(), pytest_place_as=True):
    """
    decorate(func, caller) decorates a function using a caller.
    If the caller is a generator function, the resulting function
    will be a generator function.

    You can provide additional arguments with `additional_args`. In that case
    the caller's signature should be

        `caller(f, <additional_args_in_order>, *args, **kwargs)`.

    `*args, **kwargs` will always contain the arguments required by the inner
    function `f`. If `additional_args` contains argument names that are already
    present in `func`, they will be present both in <additional_args_in_order>
    AND in `*args, **kwargs` so that it remains easy for the `caller` both to
    get the additional arguments' values directly, and to call `f` with the
    right arguments.

    Note: as of today if removed_args is not empty, positional args can not be correctly handled so all arguments
    are passed as kwargs to the wrapper

    """
    if len(additional_args) > 0:
        # wrap the caller so as to handle all cases
        # (if some additional args are already present in the signature or not)
        # so as to ensure a consistent caller signature
        caller = _wrap_caller_for_additional_args(func, caller, additional_args, removed_args)

    evaldict = dict(_call_=caller, _func_=func)
    es = ''
    for i, extra in enumerate(extras):
        ex = '_e%d_' % i
        evaldict[ex] = extra
        es += ex + ', '

    if '3.5' <= sys.version < '3.6':
        # with Python 3.5 isgeneratorfunction returns True for all coroutines
        # however we know that it is NOT possible to have a generator
        # coroutine in python 3.5: PEP525 was not there yet
        generatorcaller = isgeneratorfunction(
            caller) and not iscoroutinefunction(caller)
    else:
        generatorcaller = isgeneratorfunction(caller)
    if generatorcaller:
        fun = MyFunctionMaker.create(
            func, "for res in _call_(_func_, %s%%(shortsignature)s):\n"
                  "    yield res" % es, evaldict,
            add_args=additional_args, del_args=removed_args, __wrapped__=func)
    else:
        fun = MyFunctionMaker.create(
            func, "return _call_(_func_, %s%%(shortsignature)s)" % es,
            evaldict, add_args=additional_args, del_args=removed_args, __wrapped__=func)
    if hasattr(func, '__qualname__'):
        fun.__qualname__ = func.__qualname__

    # With this hack our decorator will be ordered correctly by pytest https://github.com/pytest-dev/pytest/issues/4429
    if pytest_place_as:
        fun.place_as = func

    return fun
