# Authors: Sylvain MARIE <sylvain.marie@se.com>
#          + All contributors to <https://github.com/smarie/python-pytest-cases>
#
# License: 3-clause BSD, <https://github.com/smarie/python-pytest-cases/blob/master/LICENSE>

# contains syntax illegal before PEP380 'Syntax for Delegating to a Subgenerator'

from makefun import wraps
from .fixture_core1_unions import is_used_request, NOT_USED


def _ignore_unused_generator_pep380(fixture_func, new_sig, func_needs_request):
    @wraps(fixture_func, new_sig=new_sig)
    def wrapped_fixture_func(*args, **kwargs):
        request = kwargs['request'] if func_needs_request else kwargs.pop('request')
        if is_used_request(request):
            yield from fixture_func(*args, **kwargs)
        else:
            yield NOT_USED

    return wrapped_fixture_func

def _decorate_fixture_plus_generator_pep380(fixture_func, new_sig, map_arguments):
    @wraps(fixture_func, new_sig=new_sig)
    def wrapped_fixture_func(*_args, **_kwargs):
        if not is_used_request(_kwargs['request']):
            yield NOT_USED
        else:
            _args, _kwargs = map_arguments(*_args, **_kwargs)
            yield from fixture_func(*_args, **_kwargs)

    return wrapped_fixture_func

def _parametrize_plus_decorate_generator_pep380(
    test_func,
    new_sig,
    fixture_union_name,
    replace_paramfixture_with_values
):
    @wraps(test_func, new_sig=new_sig)
    def wrapped_test_func(*args, **kwargs):  # noqa
        if kwargs.get(fixture_union_name, None) is NOT_USED:
            # TODO why this ? it is probably useless: this fixture
            #  is private and will never end up in another union
            yield NOT_USED
        else:
            replace_paramfixture_with_values(kwargs)
            yield from test_func(*args, **kwargs)

    return wrapped_test_func
