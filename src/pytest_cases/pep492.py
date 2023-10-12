# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>

# contains syntax illegal before PEP492 "Coroutines with async and await syntax"

from makefun import wraps
from .fixture_core1_unions import is_used_request, NOT_USED


def _ignore_unused_coroutine_pep492(fixture_func, new_sig, func_needs_request):
    @wraps(fixture_func, new_sig=new_sig)
    async def wrapped_fixture_func(*args, **kwargs):
        request = kwargs['request'] if func_needs_request else kwargs.pop('request')
        if is_used_request(request):
            return await fixture_func(*args, **kwargs)
        else:
            return NOT_USED

    return wrapped_fixture_func

def _decorate_fixture_plus_coroutine_pep492(fixture_func, new_sig, map_arguments):
    @wraps(fixture_func, new_sig=new_sig)
    async def wrapped_fixture_func(*_args, **_kwargs):
        if not is_used_request(_kwargs['request']):
            return NOT_USED
        else:
            _args, _kwargs = map_arguments(*_args, **_kwargs)
            return await fixture_func(*_args, **_kwargs)

    return wrapped_fixture_func

def _parametrize_plus_decorate_coroutine_pep492(
    test_func,
    new_sig,
    fixture_union_name,
    replace_paramfixture_with_values
):
    @wraps(test_func, new_sig=new_sig)
    async def wrapped_test_func(*args, **kwargs):  # noqa
        if kwargs.get(fixture_union_name, None) is NOT_USED:
            # TODO why this ? it is probably useless: this fixture
            #  is private and will never end up in another union
            return NOT_USED
        else:
            replace_paramfixture_with_values(kwargs)
            return await test_func(*args, **kwargs)

    return wrapped_test_func
