# Intermediate Usage 

You might feel a bit stuck when using only the basics. In particular you might feel frustrated by having to put all cases for the same function in the same dedicated file.

In this section we see that this is not mandatory at all: `pytest-cases` offers flexibility mechanisms to organize the files the way you wish.

## Gathering Cases from different files

You can gather cases from different files (modules) in the same test function:

```python
from pytest_cases import CaseDataGetter, cases_data

# the 2 modules containing cases
from . import shared_cases, shared_cases2

@cases_data(module=[shared_cases, shared_cases2])
def test_bar(case_data: CaseDataGetter):   
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    # ...
```

## Storing Cases with different purposes in the same file

This is the opposite of the above: sometimes it would just be tideous to create a **dedicated** cases file for every single test function, you just want to be able to put all of your cases in the same place, even if they are not used in the same test.

To do this we need to **associate test functions with test cases** in a more fine-grain way.

### a- Hardcoded cases list

On the test functions side, you can precisely select the required cases in `@cases_data` using `cases=<case or list of cases>`

```python
from pytest_cases import CaseDataGetter, cases_data

# the module containing the cases above
from .shared_cases import case1, case2, case3

# the 2 functions that we want to test
from mycode import foo, bar

@cases_data(cases=[case1, case2])
def test_foo(case_data: CaseDataGetter):
    """ This test will only be executed on cases tagged with 'foo'"""
    
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = foo(**i)
    assert outs == expected_o

@cases_data(cases=case3)
def test_bar(case_data: CaseDataGetter):
    """ This test will only be executed on cases tagged with 'bar'"""
    
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = bar(**i)
    assert outs == expected_o
```

In the example above, `test_foo` will be applied on `case1` and `case2`, while `test_bar` will be applied on `case3`. They can live in the same file or not, it does not matter.


### b- Simple: declare a test target

The simplest non-hardcoded approach is to use a common reference so that each test function finds the appropriate cases. The function or class under test (in other words, the "test target") might be a good idea to serve this purpose. 
 
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

On the test functions side, filter the cases in `@cases_data` using `has_tag=<target>`:

```python
from pytest_cases import CaseDataGetter, cases_data

# the module containing the cases above
from . import shared_cases

# the 2 functions that we want to test
from mycode import foo, bar

@cases_data(module=shared_cases, has_tag=foo)
def test_foo(case_data: CaseDataGetter):
    """ This test will only be executed on cases tagged with 'foo'"""
    
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it: nominal test only
    assert expected_e is None
    outs = foo(**i)
    assert outs == expected_o


@cases_data(module=shared_cases, has_tag=bar)
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

### c- Advanced: Tagging & Filtering

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

Test functions can use two things to perform their selection:

 - the `has_tag` parameter, has seen above
 - the `filter` parameter, that should be a callable taking as input a list of tags and returning a boolean.

If both are provided, a AND will be applied.

For example:

```python
from pytest_cases import THIS_MODULE, cases_data, CaseDataGetter

def has_a_or_b(tags):
    return 'a' in tags or 'b' in tags

@cases_data(module=THIS_MODULE, filter=has_a_or_b)
def test_with_cases_a_or_b(case_data: CaseDataGetter):
    # ...
```

Or with a lambda function:

```python
from pytest_cases import THIS_MODULE, cases_data, CaseDataGetter

@cases_data(module=THIS_MODULE, filter=lambda tags: 'a' in tags or 'b' in tags)
def test_with_cases_a_or_b(case_data: CaseDataGetter):
    # ...
```

Or with a mini lambda expression:

```python
from pytest_cases import THIS_MODULE, cases_data, CaseDataGetter

from mini_lambda import InputVar, _
tags = InputVar('tags', list)

@cases_data(module=THIS_MODULE, filter=_(tags.contains('a') | tags.contains('b')))
def test_with_cases_a_or_b(case_data: CaseDataGetter):
    # ...
```


## To go further

Are you at ease with the above concepts ? It's time to move to the [advanced](./advanced.md) section!
