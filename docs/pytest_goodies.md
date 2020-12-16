# `pytest` Goodies

Many `pytest` features were missing to make `pytest_cases` work with such a "no-boilerplate" experience. Many of these can be of interest to the general `pytest` audience, so they are exposed in the public API.


## `@fixture`

`@fixture` is similar to `pytest.fixture` but without its `param` and `ids` arguments. Instead, it is able to pick the parametrization from `@pytest.mark.parametrize` marks applied on fixtures. This makes it very intuitive for users to parametrize both their tests and fixtures. As a bonus, its `name` argument works even in old versions of pytest (which is not the case for `fixture`).

Finally it now supports unpacking, see [unpacking feature](#unpack_fixture-unpack_into).

!!! note "`@fixture` deprecation if/when `@pytest.fixture` supports `@pytest.mark.parametrize`"
    The ability for pytest fixtures to support the `@pytest.mark.parametrize` annotation is a feature that clearly belongs to `pytest` scope, and has been [requested already](https://github.com/pytest-dev/pytest/issues/3960). It is therefore expected that `@fixture` will be deprecated in favor of `@pytest_fixture` if/when the `pytest` team decides to add the proposed feature. As always, deprecation will happen slowly across versions (at least two minor, or one major version update) so as for users to have the time to update their code bases.

## `unpack_fixture` / `unpack_into`

In some cases fixtures return a tuple or a list of items. It is not easy to refer to a single of these items in a test or another fixture. With `unpack_fixture` you can easily do it:

```python
import pytest
from pytest_cases import unpack_fixture, fixture

@fixture
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]

a, b = unpack_fixture("a,b", c)

def test_function(a, b):
    assert a[0] == b
```

Note that you can also use the `unpack_into=` argument of `@fixture` to do the same thing:

```python
import pytest
from pytest_cases import fixture

@fixture(unpack_into="a,b")
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]

def test_function(a, b):
    assert a[0] == b
```

And it is also available in [`fixture_union`](./api_reference.md#fixture_union):

```python
import pytest
from pytest_cases import fixture, fixture_union

@fixture
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]

@fixture
@pytest.mark.parametrize("o", ['yeepee', 'yay'])
def d(o):
    return o, o[0]

fixture_union("c_or_d", [c, d], unpack_into="a, b")

def test_function(a, b):
    assert a[0] == b
```

## `param_fixture[s]`

If you wish to share some parameters across several fixtures and tests, it might be convenient to have a fixture representing this parameter. This is relatively easy for single parameters, but a bit harder for parameter tuples.

The two utilities functions `param_fixture` (for a single parameter name) and `param_fixtures` (for a tuple of parameter names) handle the difficulty for you:

```python
import pytest
from pytest_cases import param_fixtures, param_fixture

# create a single parameter fixture
my_parameter = param_fixture("my_parameter", [1, 2, 3, 4])

@pytest.fixture
def fixture_uses_param(my_parameter):
    ...

def test_uses_param(my_parameter, fixture_uses_param):
    ...

# -----
# create a 2-tuple parameter fixture
arg1, arg2 = param_fixtures("arg1, arg2", [(1, 2), (3, 4)])

@pytest.fixture
def fixture_uses_param2(arg2):
    ...

def test_uses_param2(arg1, arg2, fixture_uses_param2):
    ...
```

You can mark any of the argvalues with `pytest.mark` to pass a custom id or a custom "skip" or "fail" mark, just as you do in `pytest`. See [pytest documentation](https://docs.pytest.org/en/stable/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test).

## `fixture_union`

As of `pytest` 5, it is not possible to create a "union" fixture, i.e. a parametrized fixture that would first take all the possible values of fixture A, then all possible values of fixture B, etc. Indeed all fixture dependencies (a.k.a. "closure") of each test node are grouped together, and if they have parameters a big "cross-product" of the parameters is done by `pytest`.

The topic has been largely discussed in [pytest-dev#349](https://github.com/pytest-dev/pytest/issues/349) and a [request for proposal](https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html) has been finally made.

[`fixture_union`](./api_reference.md#fixture_union) is an implementation of this proposal. It is also used by [`@parametrize`](./api_reference.md#parametrize) to support [`fixture_ref`](./api_reference.md#fixture_ref) in parameter values, see [below](#parametrize). The theory is presented in more details in [this page](unions_theory.md), while below are more practical examples.

```python
from pytest_cases import fixture, fixture_union

@fixture
def first():
    return 'hello'

@fixture(params=['a', 'b'])
def second(request):
    return request.param

# c will first take all the values of 'first', then all of 'second'
c = fixture_union('c', [first, second])

def test_basic_union(c):
    print(c)
```

yields

```
<...>::test_basic_union[\first] hello   PASSED
<...>::test_basic_union[\second-a] a    PASSED
<...>::test_basic_union[\second-b] b    PASSED
```

### idstyle

As you can see the ids of union fixtures are slightly different from standard ids, so that you can easily understand what is going on. You can change this feature with `ìdstyle`, see [API documentation](./api_reference.md#fixture_union) for details.

### marks and ids

You can mark any of the alternatives with `pytest.mark` to pass a custom id or a custom "skip" or "fail" mark, just as you do in `pytest`. See [pytest documentation](https://docs.pytest.org/en/stable/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test).

### unpacking

Fixture unions also support unpacking with the `unpack_into` argument, see [unpacking feature](#unpack_fixture-unpack_into).

### to conclude

Fixture unions are a **major change** in the internal pytest engine, as fixture closures (the ordered set of all fixtures required by a test node to run - directly or indirectly) now become trees where branches correspond to alternative paths taken in the "unions", and leafs are the alternative fixture closures. This feature has been tested in very complex cases (several union fixtures, fixtures that are not selected by a given union but that is requested by the test function, etc.). But if you find some strange behaviour don't hesitate to report it in the [issues](https://github.com/smarie/python-pytest-cases/issues) page !

**IMPORTANT** if you do not use `@fixture` but only `@pytest.fixture`, then you will see that your fixtures are called even when they are not used, with a parameter `NOT_USED`. This symbol is automatically ignored if you use `@fixture`, otherwise you have to handle it. Alternatively you can use `@ignore_unused` on your fixture function.

!!! note "fixture unions vs. cases" 
    If you're familiar with `pytest-cases` already, you might note that `@cases_data` is not so different than a fixture union: we do a union of all case functions. If one day union fixtures are directly supported by `pytest`, we will probably refactor this lib to align all the concepts.


## `@parametrize`

[`@parametrize`](./api_reference.md#parametrize) is a replacement for `@pytest.mark.parametrize` with many additional features to make the most of parametrization. See [API reference](./api_reference.md#parametrize) for details about all the new features. In particular it allows you to include references to fixtures and to value-generating functions in the parameter values. 

 - Simply use [`fixture_ref(<fixture>)`](./api_reference.md#fixture_ref) in the parameter values, where `<fixture>` can be the fixture name or fixture function.
 - if you do not wish to create a fixture, you can also use [`lazy_value(<function>)`](./api_reference.md#lazy_value)
 - Note that when parametrizing several argnames, both [`fixture_ref`](./api_reference.md#fixture_ref) and [`lazy_value`](./api_reference.md#lazy_value) can be used *as* the tuple, or *in* the tuple. Several [`fixture_ref`](./api_reference.md#fixture_ref) and/or [`lazy_value`](./api_reference.md#lazy_value) can be used in the same tuple, too.
 - By default the id associated with a [`fixture_ref`](./api_reference.md#fixture_ref) or a [`lazy_value`](./api_reference.md#lazy_value) is the name of the fixture or function. Custom ids can be passed with the `id=<id>` parameter. 

For example, with a single argument:

```python
import pytest
from pytest_cases import parametrize, fixture, fixture_ref, lazy_value

@pytest.fixture
def world_str():
    return 'world'

def whatfun():
    return 'what'

@fixture
@parametrize('who', [fixture_ref(world_str), 
                     'you'])
def greetings(who):
    return 'hello ' + who

@parametrize('main_msg', ['nothing', 
                          fixture_ref(world_str),
                          lazy_value(whatfun),
                          "1",
                          fixture_ref(greetings)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)
```

yields the following

```bash
> pytest -s -v
collected 12 items
test_prints[nothing-?] PASSED                   [  8%]nothing?
test_prints[nothing-!] PASSED                   [ 16%]nothing!
test_prints[world_str-?] PASSED                 [ 25%]world?
test_prints[world_str-!] PASSED                 [ 33%]world!
test_prints[whatfun-?] PASSED                   [ 41%]what?
test_prints[whatfun-!] PASSED                   [ 50%]what!
test_prints[1-?] PASSED                         [ 58%]1?
test_prints[1-!] PASSED                         [ 66%]1!
test_prints[greetings-world_str-?] PASSED       [ 75%]hello world?
test_prints[greetings-world_str-!] PASSED       [ 83%]hello world!
test_prints[greetings-you-?] PASSED             [ 91%]hello you?
test_prints[greetings-you-!] PASSED             [100%]hello you!
```

### ids and marks

You can also mark any of the argvalues with `pytest.param` to pass a custom id or a custom "skip" or "fail" mark, just as you do in `pytest`. See [pytest documentation](https://docs.pytest.org/en/stable/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test).

You can also pass a custom callable or generator in `ids` as in `@pytest.mark.parametrize`.

### idstyle customization

As you can see in the example above, the default ids are similar to what you would intuitively expect, even when you use [`fixture_ref`](./api_reference.md#fixture_ref).

This is because by default `idstyle=None`, to preserve test ids very close to standard `pytest` by default. But still, a `fixture_union` is generated behind the scenes when there is a fixture reference. So this is actually non-standard. You may therefore prefer to see explicit ids showing the various fixture alternatives, as in [`fixture_union`](#fixture_union). For this simply set the `idstyle` to `'compact'`, `'explicit'` or to a callable such as `str`.

For example, changing the previous example to add `idstyle="explicit"`:

```python
(...same as above...)

@parametrize('main_msg', ['nothing',
                          fixture_ref(world_str),
                          lazy_value(whatfun),
                          "1",
                          fixture_ref(greetings)], idstyle="explicit")
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)
```

yields to 

```
> pytest -s -v
collected 12 items
test_prints[main_msg\nothing-?] PASSED                [  8%]nothing?
test_prints[main_msg\nothing-!] PASSED                [ 16%]nothing!
test_prints[main_msg\world_str-?] PASSED              [ 25%]world?
test_prints[main_msg\world_str-!] PASSED              [ 33%]world!
test_prints[main_msg\P2:4-whatfun-?] PASSED           [ 41%]what?
test_prints[main_msg\P2:4-whatfun-!] PASSED           [ 50%]what!
test_prints[main_msg\P2:4-1-?] PASSED                 [ 58%]1?
test_prints[main_msg\P2:4-1-!] PASSED                 [ 66%]1!
test_prints[main_msg\greetings-world_str-?] PASSED    [ 75%]hello world?
test_prints[main_msg\greetings-world_str-!] PASSED    [ 83%]hello world!
test_prints[main_msg\greetings-you-?] PASSED          [ 91%]hello you?
test_prints[main_msg\greetings-you-!] PASSED          [100%]hello you!
```

You can see that with this explicit style, the various "alternatives" in the fixture union generated behind the scenes for the `main_msg` parameter appear explicitly. In particular you see that there is an alternative `main_msg\P2:4` covering several parameters in a row.

Note that this `idstyle` is not taken into account if you only use [`lazy_value`](./api_reference.md#lazy_value)s but no `fixture_ref`, as `lazy_value`s do not require to create a fixture union behind the scenes.


### parametrization order

Another consequence of using [`fixture_ref`](./api_reference.md#fixture_ref) is that the priority order of the parameters, relative to other standard `pytest.mark.parametrize` parameters that you would place on the same function, will get impacted. You may solve this by replacing your other `@pytest.mark.parametrize` calls with `param_fixture`s so that all the parameters are fixtures (see [`param_fixture`](#param_fixtures)).

## passing a `hook`

As per version `1.14`, all the above functions now support passing a `hook` argument. This argument should be a callable. It will be called everytime a fixture is about to be created by `pytest_cases` on your behalf. The fixture function is passed as the argument of the hook, and the hook should return it as the result.

You can use this fixture to better understand which fixtures are created behind the scenes, and also to decorate the fixture functions before they are created. For example you can use `hook=saved_fixture` (from [`pytest-harvest`](https://smarie.github.io/python-pytest-harvest/)) in order to save the created fixtures in the fixture store.  

## `assert_exception`

`assert_exception` context manager is an alternative to `pytest.raises` to check exceptions in your tests. You can either check type, instance equality, repr string pattern, or use custom validation functions. See [API reference](./api_reference.md).

## `--with-reorder`

`pytest` postprocesses the order of the collected items in order to optimize setup/teardown of session, module and class fixtures. This optimization algorithm happens at the `pytest_collection_modifyitems` stage, and is still under improvement, as can be seen in [pytest#3551](https://github.com/pytest-dev/pytest/pull/3551), [pytest#3393](https://github.com/pytest-dev/pytest/issues/3393), [#2846](https://github.com/pytest-dev/pytest/issues/2846)...

Besides other plugins such as [pytest-reorder](https://github.com/not-raspberry/pytest_reorder) can modify the order as well.

This new commandline is a goodie to change the reordering:

 * `--with-reorder normal` is the default behaviour: it lets pytest and all the plugins execute their reordering in each of their `pytest_collection_modifyitems` hooks, and simply does not interact 
 
 * `--with-reorder skip` allows you to restore the original order that was active before `pytest_collection_modifyitems` was initially called, thus not taking into account any reordering done by pytest or by any of its plugins.
