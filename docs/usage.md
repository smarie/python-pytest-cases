# Usage

You have seen in the [main page](./index) a small example to understand the concepts. `pytest_cases` provides a few additional goodies to go further.

## Customizing case names

By default the name of the case function is used for the generated test case name. To override this, you can use the `@case_name` decorator:

```python
from pytest_cases import CaseData, case_name

@case_name("Simplest")
def case_simple_named() -> CaseData:
    """ The simplest case but with a custom name using @case_name annotation """

    ins = dict(a=1, b=2)
    outs = 2, 3

    return ins, outs, None
```

## Case generators

A case function generator is a function that will generate several test cases, once for every combination of its declared input parameters. 
 
 - The function should have at least one parameter
 - It should be decorated using `@cases_generator`, passing as keyword arguments one iterable for each parameter
 - Since all generated cases need to have a unique name, you should also provide a name template, following the [new string formatting](https://docs.python.org/3.7/library/stdtypes.html#str.format) syntax, and referencing all parameters as keyword arguments:

```python
from pytest_cases import cases_generator, CaseData

@cases_generator("case i={i}, j={j}", i=range(2), j=range(3))
def case_simple_generator(i, j) -> CaseData:
    ins = dict(a=i, b=j)
    outs = i+1, j+1
    return ins, outs, None
```

The above case generator will generate one test case for every combination of argument values, so 6 test cases:

```bash
>>> pytest
============================= test session starts =============================
(...)
<your_project>/tests/test_foo.py::test_foo[case i=0, j=0] PASSED [ 17%]
<your_project>/tests/test_foo.py::test_foo[case i=0, j=1] PASSED [ 33%]
<your_project>/tests/test_foo.py::test_foo[case i=0, j=2] PASSED [ 50%]
<your_project>/tests/test_foo.py::test_foo[case i=1, j=0] PASSED [ 67%]
<your_project>/tests/test_foo.py::test_foo[case i=1, j=1] PASSED [ 83%]
<your_project>/tests/test_foo.py::test_foo[case i=1, j=2] PASSED [ 100%]

========================== 9 passed in 0.84 seconds ==========================
```

## Handling Exceptions

Let's consider the following `foo` function under test, that may raise an exception:

```python
from math import isfinite

class InfiniteInput(Exception):
    def __init__(self, name):
        super(InfiniteInput, self).__init__(name)

    def __eq__(self, other):
        return self.args == other.args

def foo(a, b):
    """
    An example function to be tested
    
    :param a:
    :param b:
    :return:
    """
    if not isfinite(b):
        raise InfiniteInput('b')
    return a + 1, b + 1
```

`pytest_cases` proposes three ways to perform exception checking: 

 - either you provide an expected exception **type**, 
 - or an expected exception **instance**, 
 - or an exception validation **callable**.

The example below illustrates the three ways:

```python
from math import inf
from example import InfiniteInput
from pytest_cases import CaseData


def case_simple_error_type() -> CaseData:
    """ An error case with an exception type """

    ins = dict(a=1, b="a_string_not_an_int")
    err = TypeError

    return ins, None, err


def case_simple_error_instance() -> CaseData:
    """ An error case with an exception instance """

    ins = dict(a=1, b=inf)
    err = InfiniteInput('b')

    return ins, None, err


def case_simple_error_callable() -> CaseData:
    """ An error case with an exception validation callable """

    ins = dict(a=1, b=inf)
    def is_good_error(e):
        return type(e) is InfiniteInput and e.args == ('b',)

    return ins, None, is_good_error
```

In order to perform the associated assertions in your test functions, you can simply use the `unfold_expected_err` utility function bundled in `pytest_cases`:

```python
import pytest
from pytest_cases import cases_data, CaseDataGetter, unfold_expected_err
from example import foo

# import the module containing the test cases
import test_foo_cases


@cases_data(module=test_foo_cases)
def test_with_cases_decorated(case_data: CaseDataGetter):
    """ Example unit test that is automatically parametrized with @cases_data """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    if expected_e is None:
        # **** Nominal test ****
        outs = foo(**i)
        assert outs == expected_o

    else:
        # **** Error test ****
        # First see what we need to assert
        err_type, err_inst, err_checker = unfold_expected_err(expected_e)

        # Run with exception capture and type check
        with pytest.raises(err_type) as err_info:
            foo(**i)

        # Optional - Additional Exception instance check
        if err_inst is not None:
            assert err_info.value == err_inst

        # Optional - Additional exception instance check
        if err_checker is not None:
            err_checker(err_info.value)
```

## Cases in the same file than Tests

It is not mandatory that case functions should be in a different file than the test functions: both can be in the same file. For this you can use the `THIS_MODULE` constant to refer to the module in which the test function is located:

```python
from pytest_cases import CaseData, cases_data, THIS_MODULE, CaseDataGetter

def case_simple() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None

def case_simple2() -> CaseData:
    ins = dict(a=-1, b=2)
    outs = 0, 3
    return ins, outs, None

@cases_data(module=THIS_MODULE)
def test_with_cases_decorated(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    # ...
```

However **WARNING**: only the case functions located BEFORE the test function in the module file will be taken into account!


## Reusing cases in several Tests

You might wish to use the same test cases in several test functions. This works out of the box: simply refer to the same test case module in the `@case_data` decorator of several test functions, and you're set!

```python
import pytest
from pytest_cases import cases_data, CaseDataGetter

# import the module containing the test cases
import test_foo_cases


@cases_data(module=test_foo_cases)
def test_1(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()
    
    # 2- Use it
    # ...

@cases_data(module=test_foo_cases)
def test_2(case_data: CaseDataGetter):
    """ Another test that uses exactly the same test case data than test_1 """
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()
    
    # 2- Use it
    # ...
```

### Caching

After starting to reuse cases in several test functions, you might end-up thinking *"why do I have to spend the data parsing/generation time several times ? It is the same case."*. You can solve this issue by using a cache.

For simple cases you can simply decorate your case function with `@lru_cache(maxsize=1)` since simple case functions do not have parameters:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def case_a():
    # ... (as usual)
```

For case generators you **can** also use `@lru_cache(maxsize=x)`, but you will have to set the max size according to the number of generated cases (or `None` to allow auto-grow). Otherwise, simply use the `lru_cache=True` parameter and `pytest-cases` will do it for you:

```python
from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE, \
  cases_generator

# case generator with caching enabled
@cases_generator("case {i}", i=range(3), lru_cache=True)
def case_gen(i) -> CaseData:
    print("generating case " + str(i))
    ins = i
    outs, err = None, None
    return ins, outs, err

# ----------------------TESTS--------------------------

@cases_data(module=THIS_MODULE)
def test_a(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    print(i)


@cases_data(module=THIS_MODULE)
def test_b(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    print(i)
```

yields:

```bash
============================= test session starts =============================
...
collecting ... collected 6 items
test_memoize_generators.py::test_a[case 0] PASSED [ 16%]generating case 0
0
test_memoize_generators.py::test_a[case 1] PASSED [ 33%]generating case 1
1
test_memoize_generators.py::test_a[case 2] PASSED [ 50%]generating case 2
2
test_memoize_generators.py::test_b[case 0] PASSED [ 66%]0
test_memoize_generators.py::test_b[case 1] PASSED [ 83%]1
test_memoize_generators.py::test_b[case 2] PASSED [100%]2
========================== 6 passed in 0.16 seconds ===========================
```

You can see that the second time each case is needed, the cached value is used instead of executing the case generation function again.

See [doc on lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) for implementation details.

## Test cases with different purposes in the same file

Sometimes it would just be tideous to create a dedicated file to contain the case functions for each test function. However, still, it is frequent to have different test functions using different test cases. 

There is therefore a need to **associate test functions with test cases in a more fine-grain way**.

The simplest approach is to use the function under test as a common reference to bind the tests and the cases:
 
On the cases side, simply use the `@test_target` decorator:

```python
from pytest_cases import CaseData, test_target

# the 2 functions that we want to test
from mycode import foo, bar

# a case only to be used when function foo is under test
@test_target(foo)
def case_foo_simple() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None

# a case only to be used when function bar is under test
@test_target(bar)
def case_bar_simple() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None
```

On the test functions side, filter the cases in `@cases_data` using `filter=<target>`:

```python
from pytest_cases import CaseDataGetter, cases_data

# the module containing the cases above
from . import shared_cases

# the 2 functions that we want to test
from mycode import foo, bar

@cases_data(module=shared_cases, filter=foo)
def test_foo(case_data: CaseDataGetter):
    """ This test will only be executed on cases tagged with 'foo'"""
    
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = foo(**i)
    assert outs == expected_o


@cases_data(module=shared_cases, filter=bar)
def test_bar(case_data: CaseDataGetter):
    """ This test will only be executed on cases tagged with 'bar'"""
    
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = bar(**i)
    assert outs == expected_o
```

Of course this does not prevent other test functions to use all cases by not using any filter.

### Advanced: Tagging & Filtering

The above example is just a particular case of **tag** put on a case, and **filter** put on the test function. You can actually put **several** tags on the cases, not only a single one (like `@test_target` does):

```python
from pytest_cases import CaseData, case_tags

# a case with two tags
@case_tags(bar, 'fast')
def case_multitag_simple() -> CaseData:
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None
```

Test functions will be able to retrieve the above case if:

 - they do not `filter` at all
 - they use `filter=bar`
 - or they use `filter='fast'`

## Test "suites": several steps on each case 

Sometimes you wish to execute a series of tests on the same dataset, and then to move to another one. This is feasible with `pytest_cases`:

```python
from pytest_cases import test_steps, cases_data, CaseDataGetter, THIS_MODULE, \
 CaseData

# -------- test cases
def case_simple() -> CaseData:
    ins = dict(a=1, b=2)
    return ins, None, None

def case_simple2() -> CaseData:
    ins = dict(a=-1, b=2)
    return ins, None, None

# ------- test steps
def step_check_a(ins, expected_o, expected_e):
    """ Step a of the test """
    # Use the three items as usual
    print(ins)

def step_check_b(ins, expected_o, expected_e):
    """ Step b of the test """
    # Use the three items as usual
    print(ins)

# ------- test suite
@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite(test_step, case_data: CaseDataGetter):
    # Get the data for this step
    ins, expected_o, expected_e = case_data.get()

    # Execute the step
    test_step(ins, expected_o, expected_e)
```

This yields:

```bash
============================= test session starts =============================
...
test_parametrized_blend.py::test_suite[case_simple-step_check_a] PASSED  [ 25%]{'a': 1, 'b': 2}
test_parametrized_blend.py::test_suite[case_simple-step_check_b] PASSED  [ 50%]{'a': 1, 'b': 2}
test_parametrized_blend.py::test_suite[case_simple2-step_check_a] PASSED [ 75%]{'a': -1, 'b': 2}
test_parametrized_blend.py::test_suite[case_simple2-step_check_b] PASSED [100%]{'a': -1, 'b': 2}
========================== 4 passed in 0.13 seconds ===========================
```

You see that for each case, all steps are executed in order. You can wish (more rarely) to invert the order, executing all cases on step a then all cases on step b etc. Simply invert the order of decorators and it will work (`pytest` is great!).

But what if each step requires different expected output or errors ? 

```python
from pytest_cases import test_steps, cases_data, CaseDataGetter, THIS_MODULE, \
 MultipleStepsCaseData

# -------- test cases
def case_simple() -> MultipleStepsCaseData:
    ins = dict(a=1, b=2)

    outs_for_a = 2, 3
    outs_for_b = 5, 4
    outs = dict(step_check_a=outs_for_a, step_check_b=outs_for_b)

    return ins, outs, None

def case_simple2() -> MultipleStepsCaseData:
    ins = dict(a=-1, b=2)

    outs_for_a = 2, 3
    outs_for_b = 5, 4
    outs = dict(step_check_a=outs_for_a, step_check_b=outs_for_b)

    return ins, outs, None

# ------- test steps
def step_check_a(ins, expected_o, expected_e):
    """ Step a of the test """
    # Use the three items as usual
    print(ins)

def step_check_b(ins, expected_o, expected_e):
    """ Step b of the test """
    # Use the three items as usual
    print(ins)

# ------- test suite
@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite(test_step, case_data: CaseDataGetter):
    # Get the data for this step
    ins, expected_o, expected_e = case_data.get_for(test_step.__name__)

    # Execute the step
    test_step(ins, expected_o, expected_e)
```

There are two main differences with the first version:

 - in the final `test_suite` we use `case_data.get_for(test_step.__name__)` to get the case data **for a given step**
 - in the `case_simple` and `case_simple2` case functions, we provide the expected output and expected error as dictionaries, where the key is the step name.


## Advanced Pytest: Manual parametrization

The `@cases_data` decorator is just syntactic sugar for the following two-steps process, that you may wish to rely on for advanced pytest usages:

```python
import pytest
from pytest_cases import extract_cases_from_module, CaseData

# import the module containing the test cases
import test_foo_cases

# manually list the available cases
cases = extract_cases_from_module(test_foo_cases)

# parametrize the test function manually
@pytest.mark.parametrize('case_data', cases, ids=str)
def test_with_cases_decorated(case_data: CaseData):
    ...
```

Similarly the `@test_steps` decorator is equivalent to 

```python
@pytest.mark.parametrize('test_step', (step_check_a, step_check_b), ids=lambda x: x.__name__)
def test_(test_step):
    ...
```
