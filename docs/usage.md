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


## Reuse cases in several Tests

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
