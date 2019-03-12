# Usage basics

This page assumes that you have read the [initial example](../#usage).

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

## Pytest marks

Pytest marks such as `@pytest.mark.skipif` can be applied to case functions, the corresponding case will behave as expected.

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

## To go further

Are you at ease with the above concepts ? It's time to move to the [intermediate](./intermediate.md) section!
