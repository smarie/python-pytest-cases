# API reference

In general, using `help(symbol)` is the recommended way to get the latest documentation. In addition, this page provides an overview of the various elements in this package.

## 1 - Case functions

As explained in the [documentation](index.md), case functions have no requirement anymore, and starting from version 2.0.0 of `pytest_cases` they can be parametrized with the usual `@pytest.mark.parametrize` or its improvement [`@parametrize`](#parametrize). Therefore the only remaining decorator is the optional `@case` decorator:

### `@case`

```python
@case(id=None,    # type: str  # noqa
      tags=None,  # type: Union[Any, Iterable[Any]]
      marks=(),   # type: Union[MarkDecorator, Iterable[MarkDecorator]]
      )
```

Optional decorator for case functions so as to customize some information.

```python
@case(id='hey')
def case_hi():
    return 1
```

**Parameters:**

 - `id`: the custom pytest id that should be used when this case is active. Replaces the deprecated `@case_name` decorator from v1. If no id is provided, the id is generated from case functions by removing their prefix, see [`@parametrize_with_cases(prefix='case_')`](#parametrize_with_cases).

 - `tags`: custom tags to be used for filtering in [`@parametrize_with_cases(has_tags)`](#parametrize_with_cases). Replaces the deprecated `@case_tags` and `@target` decorators.
 
 - `marks`: optional pytest marks to add on the case. Note that decorating the function directly with the mark also works, and if marks are provided in both places they are merged.


## 2 - Cases collection

### `@parametrize_with_cases`

```python
@parametrize_with_cases(argnames: str,
                        cases: Union[Callable, Type, ModuleRef] = AUTO,
                        prefix: str = 'case_',
                        glob:str = None,
                        has_tag: Union[str, Iterable[str]]=None,
                        filter: Callable = None,
                        **kwargs
                        )
```

A decorator for test functions or fixtures, to parametrize them based on test cases. It works similarly to [`@pytest.mark.parametrize`](https://docs.pytest.org/en/stable/parametrize.html): argnames represent a coma-separated string of arguments to inject in the decorated test function or fixture. The argument values (`argvalues` in [`@pytest.mark.parametrize`](https://docs.pytest.org/en/stable/parametrize.html)) are collected from the various case functions found according to `cases`, and injected as lazy values so that the case functions are called just before the test or fixture is executed.

By default (`cases=AUTO`) the list of test cases is automatically drawn from the python module file named `test_<name>_cases.py` where `test_<name>` is the current module name. An alternate naming convention `cases_<name>.py` can be used by setting `cases=AUTO2`.

Finally, the `cases` argument also accepts an explicit case function, cases-containing class, module or module name; or a list of such elements. Note that both absolute and relative module names are suported.

Note that `@parametrize_with_cases` collection and parameter creation steps are strictly equivalent to [`get_all_cases`](#get_all_cases) + [`get_parametrize_args`](#get_parametrize_args). This can be handy for debugging purposes.

```python
# Collect all cases
cases_funs = get_all_cases(f, cases=cases, prefix=prefix, 
                           glob=glob, has_tag=has_tag, filter=filter)

# Transform the various functions found
argvalues = get_parametrize_args(host_class_or_module_of_f, cases_funs)
```

**Parameters**

 - `argnames`: same than in `@pytest.mark.parametrize`
 
 - `cases`: a case function, a class containing cases, a module object or a module name string (relative module names accepted). Or a list of such items. You may use `THIS_MODULE` or `'.'` to include current module. `AUTO` (default) means that the module named `test_<name>_cases.py` will be loaded, where `test_<name>.py` is the module file of the decorated function. `AUTO2` allows you to use the alternative naming scheme `case_<name>.py`. When a module is listed, all of its functions matching the `prefix`, `filter` and `has_tag` are selected, including those functions nested in classes following naming pattern `*Case*`. When classes are explicitly provided in the list, they can have any name and do not need to follow this `*Case*` pattern.

 - `prefix`: the prefix for case functions. Default is 'case_' but you might wish to use different prefixes to denote different kind of cases, for example 'data_', 'algo_', 'user_', etc.

 - `glob`: an optional glob-like pattern for case ids, for example "*_success" or "*_failure". Note that this is applied on the case id, and therefore if it is customized through [`@case(id=...)`](#case) it should be taken into account.

 - `has_tag`: a single tag or a tuple, set, list of tags that should be matched by the ones set with the [`@case`](#case) decorator on the case function(s) to be selected.

 - `filter`: a callable receiving the case function and returning True or a truth value in case the function needs to be selected.


### `get_all_cases`

```python
def get_all_cases(parametrization_target: Callable,
                  cases: Union[Callable, Type, ModuleRef] = None,
                  prefix: str = 'case_',
                  glob: str = None,
                  has_tag: Union[str, Iterable[str]] = None,
                  filter: Callable[[Callable], bool] = None
                  ) -> List[Callable]:
```

Lists all desired cases for a given `parametrization_target` (a test function or a fixture). This function may be convenient for debugging purposes. See [`@parametrize_with_cases`](#parametrize_with_cases) for details on the parameters.


### `get_parametrize_args`

```python
def get_parametrize_args(host_class_or_module: Union[Type, ModuleType],
                         cases_funs: List[Callable],
                         debug: bool = False
                         ) -> List[Union[lazy_value, fixture_ref]]:
```

Transforms a list of cases (obtained from [`get_all_cases`](#get_all_cases)) into a list of argvalues for [`@parametrize`](#parametrize). Each case function `case_fun` is transformed into one or several [`lazy_value`](#lazy_value)(s) or a [`fixture_ref`](#fixture_ref):

 - If `case_fun` requires at least on fixture, a fixture will be created if not yet present, and a `fixture_ref` will be returned.

 - If `case_fun` is a parametrized case, one `lazy_value` with a partialized version will be created for each parameter combination.

 - Otherwise, `case_fun` represents a single case: in that case a single `lazy_value` is returned.

## 3 - Pytest goodies

### `@fixture`

```python
@fixture(scope: str = "function", 
         autouse: bool = False, 
         name: str = None, 
         unpack_into: Iterable[str] = None,
         hook: Callable = None,
         **kwargs)
```

Identical to `@pytest.fixture` decorator, except that 

 - when used in a fixture union (either explicit `fixture_union` or indirect through `@parametrize`+`fixture_ref` or `@parametrize_with_cases`), it will not be setup/teardown unnecessarily in tests that do not require it.

 - it supports multi-parametrization with `@pytest.mark.parametrize` as requested in [pytest#3960](https://github.com/pytest-dev/pytest/issues/3960). As a consequence it does not support the `params` and `ids` arguments anymore.
 
 - it supports a new argument `unpack_into` where you can provide names for fixtures where to unpack this fixture into.

As a consequence it does not support the `params` and `ids` arguments anymore.

**Parameters:**

 - **scope**: the scope for which this fixture is shared, one of "function" (default), "class", "module" or "session".
 - **autouse**: if True, the fixture func is activated for all tests that can see it.  If False (the default) then an explicitreference is needed to activate the fixture.
 - **name**: the name of the fixture. This defaults to the name of the decorated function. Note: If a fixture is used in the same module in which it is defined, the function name of the fixture will be shadowed by the function arg that requests the fixture; one wayto resolve this is to name the decorated function ``fixture_<fixturename>`` and then use ``@pytest.fixture(name='<fixturename>')``.
 - **unpack_into**: an optional iterable of names, or string containing coma-separated names, for additional fixtures to create to represent parts of this fixture. See `unpack_fixture` for details.
 - **hook**: an optional hook to apply to each fixture function that is created during this call. The hook function will be called everytime a fixture is about to be created. It will receive a single argument (the function implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
 - **kwargs**: other keyword arguments for `@pytest.fixture`

### `unpack_fixture`

```python
def unpack_fixture(argnames: str,
                   fixture: Union[str, Callable],
                   hook: Callable = None
                   ) -> Tuple[<Fixture>]
```

Creates several fixtures with names `argnames` from the source `fixture`. Created fixtures will correspond to elements unpacked from `fixture` in order. For example if `fixture` is a tuple of length 2, `argnames="a,b"` will create two fixtures containing the first and second element respectively.

The created fixtures are automatically registered into the callers' module, but you may wish to assign them to variables for convenience. In that case make sure that you use the same names, e.g. `a, b = unpack_fixture('a,b', 'c')`.

```python
import pytest
from pytest_cases import unpack_fixture, fixture_plus

@fixture_plus
@pytest.mark.parametrize("o", ['hello', 'world'])
def c(o):
    return o, o[0]

a, b = unpack_fixture("a,b", c)

def test_function(a, b):
    assert a[0] == b
```

**Parameters**

 - **argnames**: same as `@pytest.mark.parametrize` `argnames`.
 - **fixture**: a fixture name string or a fixture symbol. If a fixture symbol is provided, the created fixtures will have the same scope. If a name is provided, they will have scope='function'. Note that in practice the performance loss resulting from using `function` rather than a higher scope is negligible since the created fixtures' body is a one-liner.
 - **hook**: an optional hook to apply to each fixture function that is created during this call. The hook function will be called everytime a fixture is about to be created. It will receive a single argument (the function implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.

**Outputs:** the created fixtures.

### `fixture_union`

```python
def fixture_union(name: str,
                  fixtures: Iterable[Union[str, Callable]],
                  scope: str = "function",
                  idstyle: Optional[str] = 'explicit',
                  ids: Union[Callable, List[str]] = None,
                  unpack_into: Iterable[str] = None,
                  autouse: bool = False,
                  hook: Callable = None,
                  **kwargs) -> <Fixture>
```

Creates a fixture that will take all values of the provided fixtures in order. That fixture is automatically registered into the callers' module, but you may wish to assign it to a variable for convenience. In that case make sure that you use the same name, e.g. `a = fixture_union('a', ['b', 'c'])`

The style of test ids corresponding to the union alternatives can be changed with `idstyle`. Three values are allowed:

 - `'explicit'` (default) favors readability,
 - `'compact'` adds a small mark so that at least one sees which parameters are union parameters and which others are normal parameters,
 - `None` does not change the ids.    

**Parameters:**

 - `name`: the name of the fixture to create
 - `fixtures`: an array-like containing fixture names and/or fixture symbols
 - `scope`: the scope of the union. Since the union depends on the sub-fixtures, it should be smaller than the smallest scope of fixtures referenced.
 - `idstyle`: The style of test ids corresponding to the union alternatives. One of `'explicit'` (default), `'compact'`, or `None`.
 - `unpack_into`: an optional iterable of names, or string containing coma-separated names, for additional fixtures to create to represent parts of this fixture. See `unpack_fixture` for details.
 - `ids`: as in pytest. The default value returns the correct fixture
 - `autouse`: as in pytest
 - `hook`: an optional hook to apply to each fixture function that is created during this call. The hook function will be called everytime a fixture is about to be created. It will receive a single argument (the function implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
 - `kwargs`: other pytest fixture options. They might not be supported correctly.

**Outputs:** the new fixture. Note: you do not need to capture that output in a symbol, since the fixture is automatically registered in your module. However if you decide to do so make sure that you use the same name.

### `param_fixtures`

```python
def param_fixtures(argnames: str,
                   argvalues: Iterable[Any],
                   autouse: bool = False,
                   ids: Union[Callable, List[str]] = None, 
                   scope: str = "function",
                   hook: Callable = None,
                   debug: bool = False,
                   **kwargs) -> Tuple[<Fixture>]
```

Creates one or several "parameters" fixtures - depending on the number or coma-separated names in `argnames`. The created fixtures are automatically registered into the callers' module, but you may wish to assign them to variables for convenience. In that case make sure that you use the same names, e.g. `p, q = param_fixtures('p,q', [(0, 1), (2, 3)])`.


Note that the `(argnames, argvalues, ids)` signature is similar to `@pytest.mark.parametrize` for consistency, see [pytest doc on parametrize](https://docs.pytest.org/en/latest/reference.html?highlight=pytest.param#pytest-mark-parametrize).

```python
import pytest
from pytest_cases import param_fixtures, param_fixture

# create a 2-tuple parameter fixture
arg1, arg2 = param_fixtures("arg1, arg2", [(1, 2), (3, 4)])

@pytest.fixture
def fixture_uses_param2(arg2):
    ...

def test_uses_param2(arg1, arg2, fixture_uses_param2):
    ...
```

**Parameters:**

 - `argnames`: same as `@pytest.mark.parametrize` `argnames`.
 - `argvalues`: same as `@pytest.mark.parametrize` `argvalues`.
 - `autouse`: see fixture `autouse`
 - `ids`: same as `@pytest.mark.parametrize` `ids`
 - `scope`: see fixture `scope`    
 - `hook`: an optional hook to apply to each fixture function that is created during this call. The hook function will be called everytime a fixture is about to be created. It will receive a single argument (the function implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.
 - `kwargs`: any other argument for the created 'fixtures'

### `param_fixture`

```python
param_fixture(argname, argvalues, 
              autouse=False, ids=None, hook=None, scope="function", **kwargs)
              -> <Fixture>
```

Identical to `param_fixtures` but for a single parameter name, so that you can assign its output to a single variable.


### `@parametrize`

```python
@parametrize_plus(argnames: str=None,
                  argvalues: Iterable[Any]=None,
                  indirect: bool = False,
                  ids: Union[Callable, List[str]] = None,
                  idstyle: str = 'explicit',
                  idgen: Union[str, Callable] = _IDGEN,
                  scope: str = None,
                  hook: Callable = None,
                  debug: bool = False,
                  **args)
```

Equivalent to `@pytest.mark.parametrize` but also supports 

**New alternate style for argnames/argvalues**. One can also use `**args` to pass additional `{argnames: argvalues}` in the same parametrization call. This can be handy in combination with `idgen` to master the whole id template associated with several parameters. Note that you can pass coma-separated argnames too, by de-referencing a dict: e.g. `**{'a,b': [(0, True), (1, False)], 'c': [-1, 2]}`.

**New alternate style for ids**. One can use `idgen` instead of `ids`. `idgen` can be a callable receiving all parameters at once (`**args`) and returning an id ; or it can be a string template using the new-style string formatting where the argnames can be used as variables (e.g. `idgen=lambda **args: "a={a}".format(**args)` or `idgen="my_id where a={a}"`). The special `idgen=AUTO` symbol can be used to generate a default string template equivalent to `lambda **args: "-".join("%s=%s" % (n, v) for n, v in args.items())`. This is enabled by default if you use the alternate style for argnames/argvalues (e.g. if `len(args) > 0`).

**New possibilities in argvalues**:

 - one can include *references to fixtures* with [`fixture_ref(<fixture>)`](#fixture_ref) where <fixture> can be the fixture name or fixture function. When such a fixture reference is detected in the argvalues, a new function-scope "union" fixture will be created with a unique name, and the test function will be wrapped so as to be injected with the correct parameters from this fixture. Special test ids will be created to illustrate the switching between the various normal parameters and fixtures. You can see debug print messages about all fixtures created using `debug=True`

 - one can include lazy argvalues with [`lazy_value(<valuegetter>, [id=..., marks=...])`](#lazy_value). A `lazy_value` is the same thing than a function-scoped fixture, except that the value getter function is not a fixture and therefore can neither be parametrized nor depend on fixtures. It should have no mandatory argument.

Both `fixture_ref` and `lazy_value` can be used to represent a single argvalue, or a whole tuple of argvalues when there are several argnames. Several of them can be used in a tuple.

Finally, `pytest.param` is supported even when there are `fixture_ref` and `lazy_value`. 

Here as for all functions above, an optional `hook` can be passed, to apply on each fixture function that is created during this call. The hook function will be called everytime a fixture is about to be created. It will receive a single argument (the function implementing the fixture) and should return the function to use. For example you can use `saved_fixture` from `pytest-harvest` as a hook in order to save all such created fixtures in the fixture store.

### `lazy_value`

```python
def lazy_value(valuegetter: Callable[[], Any],
               id: str = None,
               marks: Union[Any, Sequence[Any]] = ()
               ) -> LazyValue
```

A reference to a value getter (an argvalue-providing callable), to be used in [`@parametrize`](#parametrize).

A `lazy_value` is the same thing than a function-scoped fixture, except that the value getter function is not a fixture and therefore can neither be parametrized nor depend on fixtures. It should have no mandatory argument.

By default the associated id is the name of the `valuegetter` callable, but a specific `id` can be provided otherwise. Note that this `id` does not take precedence over custom `ids` or `idgen` passed to `@parametrize`.

Note that a `lazy_value` can be included in a `pytest.param` without problem. In that case the id defined by `pytest.param` will take precedence over the one defined in `lazy_value` if any. The marks, however, will all be kept wherever they are defined.

**Parameters**

 - `valuegetter`: a callable without mandatory arguments
 - `id`: an optional id. Otherwise `valuegetter.__name__` will be used by default
 - `marks`: optional marks. `valuegetter` marks will also be preserved.

### `is_lazy`

```python
def is_lazy(argval) -> bool
```

Return `True` if `argval` is the outcome of processing a `lazy_value` through `@parametrize`. This encompasses parameters that are items of lazy tuples that are created when parametrizing several argnames with the same `lazy_value()`.

### `fixture_ref`

```python
def fixture_ref(fixture: Union[str, Fixture]
                )
```

A reference to a fixture to be used with [`@parametrize`](#parametrize). Create it with `fixture_ref(<fixture>)` where <fixture> can be the fixture name or actual fixture function.
