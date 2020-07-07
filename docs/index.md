# pytest-cases

*Separate test code from test cases in `pytest`.*

[![Python versions](https://img.shields.io/pypi/pyversions/pytest-cases.svg)](https://pypi.python.org/pypi/pytest-cases/) [![Build Status](https://travis-ci.org/smarie/python-pytest-cases.svg?branch=master)](https://travis-ci.org/smarie/python-pytest-cases) [![Tests Status](https://smarie.github.io/python-pytest-cases/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-pytest-cases/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-pytest-cases/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-pytest-cases)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-pytest-cases/) [![PyPI](https://img.shields.io/pypi/v/pytest-cases.svg)](https://pypi.python.org/pypi/pytest-cases/) [![Downloads](https://pepy.tech/badge/pytest-cases)](https://pepy.tech/project/pytest-cases) [![Downloads per week](https://pepy.tech/badge/pytest-cases/week)](https://pepy.tech/project/pytest-cases) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-pytest-cases.svg)](https://github.com/smarie/python-pytest-cases/stargazers)

!!! success "Brand new v2, [check the changes](./changelog.md#200---less-boilerplate-and-full-pytest-alignment-unlocking-advanced-features) !"

!!! warning "Installing pytest-cases has effects on the order of `pytest` tests execution. Details [here](#installing)"

Did you ever think that most of your test functions were actually *the same test code*, but with *different data inputs* and expected results/exceptions ?

`pytest-cases` leverages `pytest` and its great `@pytest.mark.parametrize` decorator, so that you can **separate your test cases from your test functions**.

In addition, `pytest-cases` improves `pytest`'s fixture mechanism to support "fixture unions". This is a **major change** in the internal `pytest` engine, unlocking many possibilities such as using fixture references as parameter values in a test function. See [below](#fixture_union).

`pytest-cases` is fully compliant with [pytest-harvest](https://smarie.github.io/python-pytest-harvest/) and [pytest-steps](https://smarie.github.io/python-pytest-steps/) so you can create test suites with several steps, send each case on the full suite, and monitor the execution times and created artifacts. See [usage page for details](./usage/advanced/#test-suites-several-steps-on-each-case).

## Installing

```bash
> pip install pytest_cases
```

Note: Installing pytest-cases has effects on the order of `pytest` tests execution, even if you do not use its features. One positive side effect is that it fixed [pytest#5054](https://github.com/pytest-dev/pytest/issues/5054). But if you see less desirable ordering please [report it](https://github.com/smarie/python-pytest-cases/issues).

## Why `pytest-cases` ?

**`pytest` philosophy**

Let's consider the following `foo` function under test, located in `example.py`:

```python
def foo(a, b):
    return a + 1, b + 1
```

If we were using plain `pytest` to test it with various inputs, we would create a `test_foo.py` file and use `@pytest.mark.parametrize`:

```python
import pytest
from example import foo

@pytest.mark.parametrize("a,b", [(1, 2), (-1, -2)])
def test_foo(a, b):
    # check that foo runs correctly and that the result is a tuple. 
    assert isinstance(foo(a, b), tuple)
```

This is the fastest and most compact thing to do when you have a few number of test cases, that do not require code to generate each test case. 

**`pytest` current limitations**

Now imagine that instead of `(1, 2)` and `(-1, -2)` **each** of our test cases 

 - requires **a few lines of code** to be generated. For example artificial data creation using `numpy` and/or `pandas`:

```python
import numpy as np
import pandas as pd

# case 1: non-sorted uniformly sampled timeseries with 2 holes
case1 = pd.DataFrame({"datetime": pd.date_range(start='20/1/1', periods=20, 
                                                freq='-1d', tz='UTC'),
                      "data1": np.arange(0, 20),
                      "data2": np.arange(1, 21),
                      "data3": np.arange(1, 21)})
case1.drop([3, 12], inplace=True)
```

 - requires **documentation** to explain the other developers the intent of that precise test case

 - requires **external resources** (data files on the filesystem, databases...), with a variable number of cases depending on what is available on the resource - but of course not all the cases would come from the same resource, that would be too easy :).

 - requires **a readable `id`**, such as `'uniformly_sampled_nonsorted_with_holes'` for the above example. Of course we *could* use [`pytest.param`](https://docs.pytest.org/en/stable/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test) or [`ids=<list>`](https://docs.pytest.org/en/stable/example/parametrize.html#different-options-for-test-ids) but that is "a pain to maintain" according to `pytest` doc (I agree!). Such a design does not feel right as the id is detached from the case.

With standard `pytest` there is no particular pattern to simplify your life here. Investigating a little bit, people usually end up trying to mix parameters and fixtures and asking this kind of question: [so1](https://stackoverflow.com/questions/50231627/python-pytest-unpack-fixture), [so2](https://stackoverflow.com/questions/50482416/use-pytest-lazy-fixture-list-values-as-parameters-in-another-fixture). But by design it is not possible to solve this problem using fixtures, because `pytest` [does not handle "unions" of fixtures](#fixture_union).

So all in all, the final answer is "you have to do this yourself", and have `pytest` use your handcrafted list of parameters as the list of argvalues in `@pytest.mark.parametrize`. Typically we would end up creating a `get_all_foo_test_cases` function, independently from `pytest`:
 
```python
@pytest.mark.parametrize("a,b", get_all_foo_test_cases())
def test_foo(a, b):
    ...
```

There is also an example in `pytest` doc [with a `metafunc` hook](https://docs.pytest.org/en/stable/example/parametrize.html#a-quick-port-of-testscenarios). 

The issue with such workarounds is that you can do *anything*. And *anything* is a bit too much: this does not provide any convention / "good practice" on how to organize test cases, which is an open door to developing ad-hoc unreadable or unmaintainable solutions.

`pytest_cases` was created to provide an answer to this precise situation. It proposes a simple framework to separate test cases from test functions. The test cases are typically located in a separate "companion" file:

 - `test_foo.py` is your usual test file containing the test **functions** (named `test_<id>`),
 - `test_foo_cases.py` contains the test **cases**, that are also functions (named `case_<id>` or even `<prefix>_<id>` if you prefer). Note: an alternate file naming style `cases_foo.py` is also available if you prefer it.

![files_overview](./imgs/1_files_overview.png)

Test cases can also be provided explicitly, for example in a class container:

![class_overview](./imgs/2_class_overview.png)

And many more as we'll see [below](#d-customizing-the-cases-collection).

## Basic usage

### a- Case functions

Let's create a `test_foo_cases.py` file. This file will contain *test cases generator functions*, that we will call **case functions** for brevity. In these functions, you will typically either parse some test data files, generate some simulated test data, expected results, etc.

```python
def case_two_positive_ints():
    """ Inputs are two positive integers """
    return 1, 2

def case_two_negative_ints():
    """ Inputs are two negative integers """
    return -1, -2
```

Case functions **do not have any particular requirement**, apart from the default name convention `case_<id>` - but even that can be customized: **you can use distinct prefixes** to denote distinct kind of parameters, such as `data_<id>`, `user_<id>`, `model_<id>`... 

Case functions can return anything that is considered useful to run the associated test. We will see [below](#c-tools-for-case-functions) that you can use all classic pytest mechanism on case functions (id customization, skip/fail marks, parametrization, fixtures injection).

### b- Test functions

As usual we write our `pytest` test functions starting with `test_`, in a `test_foo.py` file. The only difference is that we now decorate it with `@parametrize_with_cases` instead of `@pytest.mark.parametrize` as we were doing [previously](#why-pytest-cases):

```python
from example import foo
from pytest_cases import parametrize_with_cases

@parametrize_with_cases("a,b")
def test_foo(a, b):
    # check that foo runs correctly and that the result is a tuple. 
    assert isinstance(foo(a, b), tuple)
```

As simple as that ! The syntax is basically the same than in [`pytest.mark.parametrize`](https://docs.pytest.org/en/stable/example/parametrize.html).

Executing `pytest` will now run our test function **once for every case function**:

```bash
>>> pytest -s -v
============================= test session starts =============================
(...)
<your_project>/tests/test_foo.py::test_foo[two_positive_ints] PASSED [ 50%]
<your_project>/tests/test_foo.py::test_foo[two_negative_ints] PASSED [ 100%]

========================== 2 passed in 0.24 seconds ==========================
```

## Tools for daily use

### a- cases collection

#### Alternate source(s)

It is not mandatory that case functions should be in a different file than the test functions: both can be in the same file. For this you can use `cases='.'` or `cases=THIS_MODULE` to refer to the module in which the test function is located:

```python
from pytest_cases import parametrize_with_cases

def case_one_positive_int():
    return 1

def case_one_negative_int():
    return -1

@parametrize_with_cases("i", cases='.')
def test_with_data(i):
    assert i == int(i)
```

However **WARNING**: only the case functions defined BEFORE the test function in the module file will be taken into account!

`@parametrize_with_cases(cases=...)` also accepts explicit list of case functions, classes containing case functions, and modules. See [API Reference](./api_reference.md#parametrize_with_cases) for details.

#### Alternate prefix

`case_` might not be your preferred prefix, especially 

 That way, you can store in the same module case functions as diverse as datasets (e.g. `data_`), user descriptions (e.g. `user_`), algorithms or machine learning models (e.g. `model_` or `algo_`), etc.

```python
from pytest_cases import parametrize_with_cases, parametrize

def data_a():
    return 'a'

@parametrize("hello", [True, False])
def data_b(hello):
    return "hello" if hello else "world"

def case_c():
    return dict(name="hi i'm not used")

@parametrize_with_cases("data", cases='.', prefix="data_")
def test_with_data(data):
    assert data in ('a', "hello", "world")
```

#### tags and filters

The easiest way to select only a subset of case functions in a module or a class, is to specify a custom `prefix` instead of the default one (`'case_'`), as shown above.

When advanced filtering is required, you can also rely on two additional mechanisms

 - use a custom `filter`

 - tag the cases with specific `tags` using the `@case` decorator, so as to filter them when collecting them in `@parametrize_with_cases`. See API reference of [`@case`](./api_reference.md#case) and [`@parametrize_with_cases`](./api_reference.md#parametrize_with_cases).



```python
from pytest_cases import parametrize_with_cases, case

class FooCases:
    def case_two_positive_ints(self):
        return 1, 2
    
    @case(tags='foo')
    def case_one_positive_int(self):
        return 1

@parametrize_with_cases("a", cases=FooCases, has_tag='foo')
def test_foo(a):
    assert a > 0
```

### b- case functions

#### custom case name

The id used by `pytest` for a given case is automatically taken from the case function name by removing any `case_` prefix. It can also be customized explicitly by decoring your case function with the `@case(id=<id>)` decorator. See [API reference](./api_reference.md#case).

```python
from pytest_cases import case

@case(id="2 positive integers")
def case_two_positive_ints():
    return 1, 2
```

#### pytest marks (`skip`, `xfail`...)

pytest marks such as `@pytest.mark.skipif` can be applied on case functions the same way [as with test functions](https://docs.pytest.org/en/stable/skipping.html).

```python
import sys
import pytest

@pytest.mark.skipif(sys.version_info < (3, 0), reason="Not useful on python 2")
def case_two_positive_ints():
    return 1, 2
```

#### case generators

In many real-world usage we want to generate one test case *per* `<something>`. The most intuitive way would be to use a `for` loop to create the case functions, and to use the `@case` decorator to set their names ; however this would not be very readable.

Instead, case functions can be parametrized the same way [as with test functions](https://docs.pytest.org/en/stable/parametrize.html): simply add the parameter names as arguments in their signature and decorate with `@pytest.mark.parametrize`. Even better, you can use the enhanced [`@parametrize`](./api_reference.md#parametrize) from `pytest-cases` so as to benefit from its additional usability features (see [API reference](./api_reference.md#parametrize)):

```python
from pytest_cases import parametrize, parametrize_with_cases

class CasesFoo:
    def case_hello(self):
        return "hello world"

    @parametrize(who=('you', 'there'))
    def case_simple_generator(self, who):
        return "hello %s" % who


@parametrize_with_cases("msg", cases=CasesFoo)
def test_foo(msg):
    assert isinstance(msg, str) and msg.startswith("hello")
```

Yields

```
test_generators.py::test_foo[hello] PASSED               [ 33%]
test_generators.py::test_foo[simple_generator-who=you] PASSED [ 66%]
test_generators.py::test_foo[simple_generator-who=there] PASSED [100%]
```

#### cases requiring fixtures

Cases can use fixtures the same way as [test functions do](https://docs.pytest.org/en/stable/fixture.html#fixtures-as-function-arguments): simply add the fixture names as arguments in their signature and make sure the fixture exists either in the same module, or in a [`conftest.py`](https://docs.pytest.org/en/stable/fixture.html?highlight=conftest.py#conftest-py-sharing-fixture-functions) file in one of the parent packages. See [`pytest` documentation on sharing fixtures](https://docs.pytest.org/en/stable/fixture.html?highlight=conftest.py#conftest-py-sharing-fixture-functions).


```python
from pytest_cases import parametrize_with_cases, fixture, parametrize

@fixture(scope='session')
def db():
    return {0: 'louise', 1: 'bob'}

def user_bob(db):
    return db[1]

@parametrize(id=range(2))
def user_from_db(db, id):
    return db[id]

@parametrize_with_cases("a", cases='.', prefix='user_')
def test_users(a, db, request):
    print("this is test %r" % request.node.nodeid)
    assert a in db.values()
```

yields

```
test_fixtures.py::test_users[a_is_bob] 
test_fixtures.py::test_users[a_is_from_db-id=0] 
test_fixtures.py::test_users[a_is_from_db-id=1] 
```

### c- Test fixtures

In some scenarii you might wish to parametrize a fixture rather than the test function. For example 

 - to inject the test cases in several test functions without copying `@parametrize_with_cases`
 - to modify the test cases or log some message, etc. before injecting them into the test functions
 - ...

For this, simply use `@fixture` from `pytest_cases` instead of `@pytest.fixture` to define your fixture. That allows your fixtures to be easily parametrized with `@parametrize_with_cases`, `@parametrize`, and even `@pytest.mark.parametrize`.


```python
from pytest_cases import fixture, parametrize_with_cases

@fixture
@parametrize_with_cases("a,b")
def c(a, b):
    return a + b

def test_foo(c):
    assert isinstance(c, int)
```


## `pytest` Goodies

Many `pytest` features were missing to make `pytest_cases` work. Many of these can be of interest to the general `pytest` audience, so they are exposed in the public API.


### `@fixture`

`@fixture` is similar to `pytest.fixture` but without its `param` and `ids` arguments. Instead, it is able to pick the parametrization from `@pytest.mark.parametrize` marks applied on fixtures. This makes it very intuitive for users to parametrize both their tests and fixtures. As a bonus, its `name` argument works even in old versions of pytest (which is not the case for `fixture`).

Finally it now supports unpacking, see [unpacking feature](#unpack_fixture-unpack_into).

!!! note "`@fixture` deprecation if/when `@pytest.fixture` supports `@pytest.mark.parametrize`"
    The ability for pytest fixtures to support the `@pytest.mark.parametrize` annotation is a feature that clearly belongs to `pytest` scope, and has been [requested already](https://github.com/pytest-dev/pytest/issues/3960). It is therefore expected that `@fixture` will be deprecated in favor of `@pytest_fixture` if/when the `pytest` team decides to add the proposed feature. As always, deprecation will happen slowly across versions (at least two minor, or one major version update) so as for users to have the time to update their code bases.

### `unpack_fixture` / `unpack_into`

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

And it is also available in `fixture_union`:

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

### `param_fixture[s]`

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

### `fixture_union`

As of `pytest` 5, it is not possible to create a "union" fixture, i.e. a parametrized fixture that would first take all the possible values of fixture A, then all possible values of fixture B, etc. Indeed all fixture dependencies (a.k.a. "closure") of each test node are grouped together, and if they have parameters a big "cross-product" of the parameters is done by `pytest`.

The topic has been largely discussed in [pytest-dev#349](https://github.com/pytest-dev/pytest/issues/349) and a [request for proposal](https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html) has been finally made.

`fixture_union` is an implementation of this proposal. It is also used by `parametrize` to support `fixture_ref` in parameter values, see [below](#parametrize).

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
<...>::test_basic_union[c_is_first] hello   PASSED
<...>::test_basic_union[c_is_second-a] a    PASSED
<...>::test_basic_union[c_is_second-b] b    PASSED
```

As you can see the ids of union fixtures are slightly different from standard ids, so that you can easily understand what is going on. You can change this feature with `ìdstyle`, see [API documentation](./api_reference.md#fixture_union) for details.

You can mark any of the alternatives with `pytest.mark` to pass a custom id or a custom "skip" or "fail" mark, just as you do in `pytest`. See [pytest documentation](https://docs.pytest.org/en/stable/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test).

Fixture unions also support unpacking with the `unpack_into` argument, see [unpacking feature](#unpack_fixture-unpack_into).

Fixture unions are a **major change** in the internal pytest engine, as fixture closures (the ordered set of all fixtures required by a test node to run - directly or indirectly) now become trees where branches correspond to alternative paths taken in the "unions", and leafs are the alternative fixture closures. This feature has been tested in very complex cases (several union fixtures, fixtures that are not selected by a given union but that is requested by the test function, etc.). But if you find some strange behaviour don't hesitate to report it in the [issues](https://github.com/smarie/python-pytest-cases/issues) page !

**IMPORTANT** if you do not use `@fixture` but only `@pytest.fixture`, then you will see that your fixtures are called even when they are not used, with a parameter `NOT_USED`. This symbol is automatically ignored if you use `@fixture`, otherwise you have to handle it. Alternatively you can use `@ignore_unused` on your fixture function.

!!! note "fixture unions vs. cases" 
    If you're familiar with `pytest-cases` already, you might note that `@cases_data` is not so different than a fixture union: we do a union of all case functions. If one day union fixtures are directly supported by `pytest`, we will probably refactor this lib to align all the concepts.


### `@parametrize`

`@parametrize` is a replacement for `@pytest.mark.parametrize` with many additional features to make the most of parametrization. See [API reference](./api_reference.md#parametrize) for details about all the new features. In particular it allows you to include references to fixtures and to value-generating functions in the parameter values. 

 - Simply use `fixture_ref(<fixture>)` in the parameter values, where `<fixture>` can be the fixture name or fixture function.
 - if you do not wish to create a fixture, you can also use `lazy_value(<function>)`
 - Note that when parametrizing several argnames, both `fixture_ref` and `lazy_value` can be used *as* the tuple, or *in* the tuple. Several `fixture_ref` and/or `lazy_value` can be used in the same tuple, too. 

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
                               fixture_ref(greetings)])
@pytest.mark.parametrize('ending', ['?', '!'])
def test_prints(main_msg, ending):
    print(main_msg + ending)
```

yields the following

```bash
> pytest -s -v
collected 10 items
test_prints[main_msg_is_nothing-?] PASSED       [ 10%]nothing?
test_prints[main_msg_is_nothing-!] PASSED       [ 20%]nothing!
test_prints[main_msg_is_world_str-?] PASSED     [ 30%]world?
test_prints[main_msg_is_world_str-!] PASSED     [ 40%]world!
test_prints[main_msg_is_whatfun-?] PASSED       [ 50%]what?
test_prints[main_msg_is_whatfun-!] PASSED       [ 60%]what!
test_prints[main_msg_is_greetings-who_is_world_str-?] PASSED [ 70%]hello world?
test_prints[main_msg_is_greetings-who_is_world_str-!] PASSED [ 80%]hello world!
test_prints[main_msg_is_greetings-who_is_you-?] PASSED [ 90%]hello you?
test_prints[main_msg_is_greetings-who_is_you-!] PASSED [100%]hello you!
```

You can also mark any of the argvalues with `pytest.mark` to pass a custom id or a custom "skip" or "fail" mark, just as you do in `pytest`. See [pytest documentation](https://docs.pytest.org/en/stable/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test).

As you can see in the example above, the default ids are a bit more explicit than usual when you use at least one `fixture_ref`. This is because the parameters need to be replaced with a fixture union that will "switch" between alternative groups of parameters, and the appropriate fixtures referenced. As opposed to `fixture_union`, the style of these ids is not configurable for now, but feel free to propose alternatives in the [issues page](https://github.com/smarie/python-pytest-cases/issues). Note that this does not happen if you only use `lazy_value`s, as they do not require to create a fixture union behind the scenes.

Another consequence of using `fixture_ref` is that the priority order of the parameters, relative to other standard `pytest.mark.parametrize` parameters that you would place on the same function, will get impacted. You may solve this by replacing your other `@pytest.mark.parametrize` calls with `param_fixture`s so that all the parameters are fixtures (see [above](#param_fixtures).)

### passing a `hook`

As per version `1.14`, all the above functions now support passing a `hook` argument. This argument should be a callable. It will be called everytime a fixture is about to be created by `pytest_cases` on your behalf. The fixture function is passed as the argument of the hook, and the hook should return it as the result.

You can use this fixture to better understand which fixtures are created behind the scenes, and also to decorate the fixture functions before they are created. For example you can use `hook=saved_fixture` (from [`pytest-harvest`](https://smarie.github.io/python-pytest-harvest/)) in order to save the created fixtures in the fixture store.  

### `assert_exception`

`assert_exception` context manager is an alternative to `pytest.raises` to check exceptions in your tests. You can either check type, instance equality, repr string pattern, or use custom validation functions. See [API reference](./api_reference.md).

### `--with-reorder`

`pytest` postprocesses the order of the collected items in order to optimize setup/teardown of session, module and class fixtures. This optimization algorithm happens at the `pytest_collection_modifyitems` stage, and is still under improvement, as can be seen in [pytest#3551](https://github.com/pytest-dev/pytest/pull/3551), [pytest#3393](https://github.com/pytest-dev/pytest/issues/3393), [#2846](https://github.com/pytest-dev/pytest/issues/2846)...

Besides other plugins such as [pytest-reorder](https://github.com/not-raspberry/pytest_reorder) can modify the order as well.

This new commandline is a goodie to change the reordering:

 * `--with-reorder normal` is the default behaviour: it lets pytest and all the plugins execute their reordering in each of their `pytest_collection_modifyitems` hooks, and simply does not interact 
 
 * `--with-reorder skip` allows you to restore the original order that was active before `pytest_collection_modifyitems` was initially called, thus not taking into account any reordering done by pytest or by any of its plugins.

## Main features / benefits

 * **Separation of concerns**: test code on one hand, test cases data on the other hand. This is particularly relevant for data science projects where a lot of test datasets are used on the same block of test code.
 
 * **Everything in the test or in the fixture**, not outside. A side-effect of `@pytest.mark.parametrize` is that users tend to create or parse their datasets outside of the test function. `pytest_cases` suggests a model where the potentially time and memory consuming step of case data generation/retrieval is performed *inside* the test node or the required fixture, thus keeping every test case run more independent. It is also easy to put debug breakpoints on specific test cases.

 * **Easier iterable-based test case generation**. If you wish to generate several test cases using the same function, `@cases_generator` makes it very intuitive to do so. See [here](./usage#case-generators) for details.

 * **User-friendly features**: easily customize your test cases with friendly names, reuse the same cases for different test functions by tagging/filtering, and more... See [Usage](./usage) for details.

## See Also

 - [pytest documentation on parametrize](https://docs.pytest.org/en/latest/parametrize.html)
 - [pytest documentation on fixtures](https://docs.pytest.org/en/latest/fixture.html#fixture-parametrize)
 - [pytest-steps](https://smarie.github.io/python-pytest-steps/)
 - [pytest-harvest](https://smarie.github.io/python-pytest-harvest/)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-pytest-cases](https://github.com/smarie/python-pytest-cases)
