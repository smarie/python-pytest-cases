# pytest-cases

*Separate test code from test cases in `pytest`.*

[![Build Status](https://travis-ci.org/smarie/python-pytest-cases.svg?branch=master)](https://travis-ci.org/smarie/python-pytest-cases) [![Tests Status](https://smarie.github.io/python-pytest-cases/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-pytest-cases/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-pytest-cases/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-pytest-cases) [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://smarie.github.io/python-pytest-cases/) [![PyPI](https://img.shields.io/badge/PyPI-pytest_cases-blue.svg)](https://pypi.python.org/pypi/pytest_cases/)

Did you ever thought that most of your test functions were actually *the same test code*, but with *different data inputs* and expected results/exceptions ?

`pytest-cases` leverages `pytest` and its great `@pytest.mark.parametrize` decorator, so that you can **separate your test cases from your test functions**. For example with `pytest-cases` you can now write your tests with the following pattern:

 * on one hand, the usual `test_xxxx.py` file containing your test functions
 * on the other hand, a new `test_xxxx_cases.py` containing your cases functions


## Installing

```bash
> pip install pytest_cases
```

## Usage
 
### a- Some code to test

Let's consider the following `foo` function under test:

```python
def foo(a, b):
    return a + 1, b + 1
```

### b- Case functions

First we create a `test_foo_cases.py` file. This file will contain *test cases generator* functions, that we will call **case functions** for brevity:

```python
from pytest_cases import CaseData

def case_two_positive_ints() -> CaseData:
    """ Inputs are two positive integers """

    ins = dict(a=1, b=2)
    outs = 2, 3

    return ins, outs, None

def case_two_negative_ints() -> CaseData:
    """ Inputs are two negative integers """

    ins = dict(a=-1, b=-2)
    outs = 0, -1

    return ins, outs, None
```

In these functions, you will typically either parse some test data files, or generate some simulated test data and expected results. 

Case functions **do not have any particular requirement**, apart from their names starting with `case_`. They can return anything that is considered useful to run the associated test. 

However, as shown in the example above, `pytest_cases` proposes to adopt a convention where the functions always returns a tuple of inputs/outputs/errors. A handy `CaseData` PEP484 type hint can be used to denote that.

### c- Test functions

Finally, as usual we write our `pytest` functions starting with `test_`, in a `test_foo.py` file:

```python
from pytest_cases import cases_data, CaseData
from example import foo

# import the module containing the test cases
import test_foo_cases


@cases_data(module=test_foo_cases)
def test_foo(case_data: CaseData):
    """ Example unit test that is automatically parametrized with @cases_data """

    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    if expected_e is None:
        # **** Nominal test ****
        outs = foo(**i)
        assert outs == expected_o

    else:
        # **** Error tests: see <Usage> page to fill this ****
        pass
```

As you can see above there are three things that are needed to bind a test function with associated case functions:

 * decorate your test function with `@cases_data`, indicating which module contains the cases functions
 * add an input argument to your test function, named `case_data` with optional type hint `CaseData`
 * use that input argument at the beginning of the test function, to retrieve the test data: `i, expected_o, expected_e = case_data.get()`


Once you have done these three steps, executing `pytest` will run your test function **once for every case function**:

```bash
>>> pytest
============================= test session starts =============================
(...)
<your_project>/tests/test_foo.py::test_foo[case_two_positive_ints] PASSED [ 50%]
<your_project>/tests/test_foo.py::test_foo[case_two_negative_ints] PASSED [ 100%]

========================== 2 passed in 0.24 seconds ==========================
```


See [Usage](./usage) for a complete example with exceptions handling and more.


## Main features / benefits

 * **Separation of concerns**: test code on one hand, test cases data on the other hand. This is particularly relevant for data science projects where a lot of test datasets are used on the same block of test code.
 
 * **Everything in the test**, not outside. A side-effect of `@pytest.mark.parametrize` is that users tend to create or parse their datasets outside of the test function. `pytest_cases` suggests a model where the potentially time and memory consuming step of case data gathering is performed *inside* the test case, thus keeping every test case run more independent.


## See Also

[pytest documentation on parametrize](https://docs.pytest.org/en/latest/parametrize.html)

### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie?utf8=%E2%9C%93&tab=repositories&q=&type=&language=python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-pytest-cases](https://github.com/smarie/python-pytest-cases)
