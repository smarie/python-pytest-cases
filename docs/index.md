# pytest-cases

*Separate test code from test cases in `pytest`.*

[![Python versions](https://img.shields.io/pypi/pyversions/pytest-cases.svg)](https://pypi.python.org/pypi/pytest-cases/) [![Build Status](https://travis-ci.org/smarie/python-pytest-cases.svg?branch=master)](https://travis-ci.org/smarie/python-pytest-cases) [![Tests Status](https://smarie.github.io/python-pytest-cases/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-pytest-cases/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-pytest-cases/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-pytest-cases)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-pytest-cases/) [![PyPI](https://img.shields.io/pypi/v/pytest-cases.svg)](https://pypi.python.org/pypi/pytest-cases/) [![Downloads](https://pepy.tech/badge/pytest-cases)](https://pepy.tech/project/pytest-cases) [![Downloads per week](https://pepy.tech/badge/pytest-cases/week)](https://pepy.tech/project/pytest-cases) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-pytest-cases.svg)](https://github.com/smarie/python-pytest-cases/stargazers)

!!! success "New `@pytest_fixture_plus` decorator is there, [check it out](#d-case-fixtures) !"

Did you ever thought that most of your test functions were actually *the same test code*, but with *different data inputs* and expected results/exceptions ?

`pytest-cases` leverages `pytest` and its great `@pytest.mark.parametrize` decorator, so that you can **separate your test cases from your test functions**. For example with `pytest-cases` you can now write your tests with the following pattern:

 * on one hand, the usual `test_xxxx.py` file containing your test functions
 * on the other hand, a new `test_xxxx_cases.py` containing your cases functions

`pytest-cases` is fully compliant with [pytest-steps](https://smarie.github.io/python-pytest-steps/) so you can create test suites with several steps and send each case on the full suite. See [usage page for details](./usage/advanced/#test-suites-several-steps-on-each-case).


## Installing

```bash
> pip install pytest_cases
```

## Usage - 'Data' cases
 
### a- Some code to test

Let's consider the following `foo` function under test:

```python
def foo(a, b):
    return a + 1, b + 1
```

### b- Case functions

First we create a `test_foo_cases.py` file. This file will contain *test cases generator* functions, that we will call **case functions** for brevity:

```python
def case_two_positive_ints():
    """ Inputs are two positive integers """
    return dict(a=1, b=2)

def case_two_negative_ints():
    """ Inputs are two negative integers """
    return dict(a=-1, b=-2)
```

In these functions, you will typically either parse some test data files, or generate some simulated test data and expected results. 

Case functions **do not have any particular requirement**, apart from their names starting with `case_`. They can return anything that is considered useful to run the associated test. 


!!! note "Support for pytest marks"
    Pytest marks such as `@pytest.mark.skip` can be used on case functions, the corresponding case will be handled according to the expected behaviour (failed if `@pytest.mark.fail`, skipped under condition if `@pytest.mark.skipif`, etc.)

    
### c- Test functions

Then, as usual we write our `pytest` functions starting with `test_`, in a `test_foo.py` file:

```python
from pytest_cases import cases_data
from example import foo

# import the module containing the test cases
import test_foo_cases

@cases_data(module=test_foo_cases)
def test_foo(case_data):
    """ Example unit test that is automatically parametrized with @cases_data """

    # 1- Grab the test case data
    inputs = case_data.get()

    # 2- Use it
    foo(**inputs)
```

*Note: as explained [here](https://smarie.github.io/python-pytest-cases/usage/basics/#cases-in-the-same-file-than-tests), cases can also be located inside the test file.*

As you can see above there are three things that are needed to parametrize a test function with associated case functions:

 * decorate your test function with `@cases_data`, indicating which module contains the cases functions
 * add an input argument to your test function, named `case_data` with optional type hint `CaseData`
 * use that input argument at the beginning of the test function, to retrieve the test data: `inputs = case_data.get()`


Once you have done these three steps, executing `pytest` will run your test function **once for every case function**:

```bash
>>> pytest
============================= test session starts =============================
(...)
<your_project>/tests/test_foo.py::test_foo[case_two_positive_ints] PASSED [ 50%]
<your_project>/tests/test_foo.py::test_foo[case_two_negative_ints] PASSED [ 100%]

========================== 2 passed in 0.24 seconds ==========================
```

### d- Case fixtures

You might be concerned that case data is gathered or created *during* test execution. 

Indeed creating or collecting case data is not part of the test *per se*. Besides, if you benchmark your tests durations (for example with [pytest-harvest](https://smarie.github.io/python-pytest-harvest/)), you may want the test duration to be computed without acccounting for the data retrieval time - especially if you decide to add some caching mechanism as explained [here](https://smarie.github.io/python-pytest-cases/usage/advanced/#caching).

It might therefore be more interesting for you to parametrize **case fixtures** instead of parametrizing your test function:

```python
from pytest_cases import pytest_fixture_plus, cases_data
from example import foo

# import the module containing the test cases
import test_foo_cases

@pytest_fixture_plus
@cases_data(module=test_foo_cases)
def inputs(case_data):
    """ Example fixture that is automatically parametrized with @cases_data """
    # retrieve case data
    return case_data.get()

def test_foo(inputs):
    # Use case data
    foo(**inputs)
```

In the above example, the `test_foo` test does not spend time collecting or generating data. When it is executed, it receives the required data directly as `inputs`. The test case creation instead happens when each `inputs` fixture instance is created by `pytest` - this is done in a separate pytest phase (named "setup"), and therefore is not counted in the test duration.

Note: you can still use `request` in your fixture's signature if you wish to.

!!! note "`@pytest_fixture_plus` deprecation if/when `@pytest.fixture` supports `@pytest.mark.parametrize`"
    The ability for pytest fixtures to support the `@pytest.mark.parametrize` annotation is a feature that clearly belongs to `pytest` scope, and has been [requested already](https://github.com/pytest-dev/pytest/issues/3960). It is therefore expected that `@pytest_fixture_plus` will be deprecated in favor of `@pytest_fixture` if/when the `pytest` team decides to add the proposed feature. As always, deprecation will happen slowly across versions (at least two minor, or one major version update) so as for users to have the time to update their code bases.

## Usage - 'True' test cases

#### a- Case functions update

In the above example the cases were only containing inputs for the function to test. In real-world applications we often need more: we need both inputs **and an expected outcome**. 

For this, `pytest_cases` proposes to adopt a convention where the case functions returns a tuple of inputs/outputs/errors. A handy `CaseData` PEP484 type hint can be used to denote that. But of course this is only a proposal, which is not mandatory as we saw above.

!!! note "A case function can return **anything**"
    Even if in most examples in this documentation we chose to return a tuple (inputs/outputs/errors) (type hint `CaseData`), you can decide to return anything: a single variable, a dictionary, a tuple of a different length, etc. Whatever you return will be available through `case_data.get()`.

Here is how we can rewrite our case functions with an expected outcome:

```python
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

We propose that the "expected error" (`None` above) may contain exception type, exception instances, or callables. If you follow this convention, you will be able to write your test more easily with the provided utility function `unfold_expected_err`. See [here for details](https://smarie.github.io/python-pytest-cases/usage/basics/#handling-exceptions).

### b- Test body update

With our new case functions, a case will be made of three items. So `case_data.get()` will return a tuple. Here is how we can update our test function body to retrieve it correctly, and check that the outcome is as expected:

```python
@cases_data(module=test_foo_cases)
def test_foo(case_data: CaseDataGetter):
    """ Example unit test that is automatically parametrized with @cases_data """

    # 1- Grab the test case data: now a tuple !
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: we can now do some asserts !
    if expected_e is None:
        # **** Nominal test ****
        outs = foo(**i)
        assert outs == expected_o
    else:
        # **** Error tests: see <Usage> page to fill this ****
        pass
```

See [Usage](./usage) for complete examples with custom case names, case generators, exceptions handling, and more.


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
