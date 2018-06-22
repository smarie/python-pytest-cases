# Usage

You have seen in the [main page] a small example to understand the concepts. `pytest_cases` provides a few additional goodies to go further.

## Customizing case names

You can use the `@case_name` decorator on any case generator function to customize the resulting pytest case name:

```python
from pytest_cases import CaseData, case_name


@case_name("Simplest")
def case_simple_named() -> CaseData:
    """ The simplest case but with a custom name using @case_name annotation """

    ins = dict(a=1, b=2)
    outs = 2, 3

    return ins, outs, None
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

`pytest_cases` proposes three ways to perform exception checking: either you provide an expected exception type, or an expected exception instance, or a callable.

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

Then you can use `unfold_expected_err` in your test functions in order to perform some reasoning on the exception, as shown below:

```python
import pytest
from pytest_cases import cases_data, CaseData, unfold_expected_err
from example import foo

# import the module containing the test cases
import test_foo_cases


@cases_data(module=test_foo_cases)
def test_with_cases_decorated(case_data: CaseData):
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
        err_type, err_inst, err_checker = unfold_expected_err(expected_e)

        # Exception capture and type check
        with pytest.raises(err_type) as err_info:
            foo(**i)

        # Optional - Additional Exception instance check
        if err_inst is not None:
            assert err_info.value == err_inst

        # Optional - Additional exception instance check
        if err_checker is not None:
            err_checker(err_info.value)
```


## Manual parametrization

The `@cases_data` decorator is just syntactic sugar for the following two-steps process, that you may wish to rely on for advanced usage:

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
