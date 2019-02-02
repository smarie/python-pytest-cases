# API reference

In general, using `help(symbol)` is the recommended way to get the latest documentation. In addition, this page provides an overview of the various elements in this package.


## 1 - On case functions side

### `CaseData` type hint

A proposed standard type hint for the case functions outputs. `CaseData = Tuple[Given, ExpectedNormal, ExpectedError]` where 

```python
Given = Any
"""The input(s) for the test. It can be anything"""

ExpectedNormal = Optional[Any]
"""The expected test results in case success is expected, or None if this test
 should fail"""

ExpectedError = Optional[Union[Type[Exception], 
                               Exception, 
                               Callable[[Exception], Optional[bool]]]]
"""The expected error in case failure is expected, or None if the test should 
succeed. It is proposed that expected error can be defined as an exception 
type, an exception instance, or an exception validation function"""
```

### `@case_name`

`@case_name(name: str)`

Decorator to override the name of a case function. The new name will be used instead of the function name, in test names.

```python
@case_name('simple_case')
def case_simple():
    ...
```

### `@case_tags`

`@case_tags(*tags: Any)`

Decorator to tag a case function with a list of tags. These tags can then be used in the `@cases_data` test function decorator to filter cases within the selected module(s).

**Parameters:**

 - `tags`: a list of tags that may be used to filter the case. Tags can be anything (string, objects, types, functions...)


### `@test_target`

`@test_target(target: Any)`

A simple decorator to declare that a case function is associated with a particular target.

```python
@test_target(int)
def case_to_test_int():
    ...
```

This is actually an alias for `@case_tags(target)`, that some users may find a bit more readable.


### `@cases_generator`

`@cases_generator(name_template: str, lru_cache: bool=False, **param_ranges)`

Decorator to declare a case function as being a cases generator. `param_ranges`  should be a named list of parameter ranges to explore to generate the cases.
    
The decorator will use `itertools.product` to create a cartesian product of the named parameter ranges, and create a case for each combination. When the case function will be called for a given combination, the corresponding parameters will be passed to the decorated function.

```python
@cases_generator("test with i={i}", i=range(10))
def case_10_times(i):
    ''' Generates 10 cases '''
    ins = dict(a=i, b=i+1)
    outs = i+1, i+2
    return ins, outs, None
```

**Parameters:**

 - `name_template`: a name template, that will be transformed into the case name using `name_template.format(**params)` for each case, where params is the dictionary of parameter values for this generated case.
 - `lru_cache`: a boolean (default False) indicating if the generated cases should be cached. This is identical to decorating the function with an additional `@lru_cache(maxsize=n)` where n is the total number of generated cases.
 - `param_ranges`: named parameters and for each of them the list of values to be used to generate cases. For each combination of values (a cartesian product is made) the parameters will be passed to the underlying function so they should have names the underlying function can handle. 


### `MultipleStepsCaseData` type hint

You may wish to use this type hint instead of `CaseData` when your case functions may return dictionaries of given/expected_normal/expected_error.

`MultipleStepsCaseData = Tuple[Union[Given, Dict[Any, Given]],
                               Union[ExpectedNormal, Dict[Any, ExpectedNormal]],
                               Union[ExpectedError, Dict[Any, ExpectedError]]]`

## 2 - On test functions side

### `@cases_fixture`

`@cases_fixture(cases=None, module=None, case_data_argname='case_data', has_tag=None, filter=None)`

Decorates a function so that it becomes a parametrized fixture.

The fixture will be automatically parametrized with all cases listed in module `module`, or with
all cases listed explicitly in `cases`.

Using it with a non-None `module` argument is equivalent to
 * extracting all cases from `module`
 * then decorating your function with @pytest.fixture(params=cases) with all the cases

So

```python
from pytest_cases import cases_fixture, CaseData

# import the module containing the test cases
import test_foo_cases

@cases_fixture(module=test_foo_cases)
def foo_fixture(case_data: CaseData):
    ...
```

is equivalent to:

```python
import pytest
from pytest_cases import get_all_cases, get_pytest_parametrize_args

# import the module containing the test cases
import test_foo_cases

# manually list the available cases
cases = get_all_cases(module=test_foo_cases)

# transform into required arguments for pytest (applying the pytest marks if needed)
marked_cases, cases_ids = get_pytest_parametrize_args(cases)

# parametrize the fixture manually
@pytest.fixture(params=marked_cases, ids=cases_ids)
def foo_fixture(request):
    case_data = request.param  # type: CaseData
    ...
```

**Parameters**

 - `case_data_argname`: the optional name of the function parameter that should receive the `CaseDataGetter` object. Default is `case_data`.
 - Other parameters (cases, module, has_tag, filter) can be used to perform explicit listing, or filtering, of cases to include. See `get_all_cases()` for details about them.

### `@cases_data`

`@cases_data(cases=None, module=None, case_data_argname='case_data', has_tag=None, filter=None)`

Decorates a test function so as to automatically parametrize it with all cases listed in module `module`, or with all cases listed explicitly in `cases`.

Using it with a non-None `module` argument is equivalent to

 * extracting all cases from `module`
 * then decorating your function with `@pytest.mark.parametrize` with all the cases

So

```python
from pytest_cases import cases_data

# import the module containing the test cases
import test_foo_cases

@cases_data(module=test_foo_cases)
def test_foo(case_data):
    ...
```
 
is equivalent to:

```python
import pytest
from pytest_cases import get_all_cases, get_pytest_parametrize_args

# import the module containing the test cases
import test_foo_cases

# manually list the available cases
cases = get_all_cases(module=test_foo_cases)

# transform into required arguments for pytest (applying the pytest marks if needed)
marked_cases, cases_ids = get_pytest_parametrize_args(cases)

# parametrize the test function manually
@pytest.mark.parametrize('case_data', marked_cases, ids=str)
def test_foo(case_data):
    ...
```

**Parameters**

 - `case_data_argname`: the optional name of the function parameter that should receive the `CaseDataGetter` object. Default is `case_data`.
 - Other parameters (cases, module, has_tag, filter) can be used to perform explicit listing, or filtering, of cases to include. See `get_all_cases()` for details about them.

### `CaseDataGetter`

A proxy for a test case. Instances of this class are created by `@cases_data` or `get_all_cases`. It provides a single method:

`get(self, *args, **kwargs) -> Union[CaseData, Any]`

This method calls the actual underlying case function with arguments propagation, and returns the result. The case functions can use the proposed standard `CaseData` type hint and return outputs matching this type hint, but this is not mandatory.

### `unfold_expected_err`

'Unfolds' the expected error `expected_e` to return a tuple of

 - expected error type
 - expected error instance
 - error validation callable

If `expected_e` is an exception type, returns `expected_e, None, None`.
If `expected_e` is an exception instance, returns `type(expected_e), expected_e, None`.
If `expected_e` is an exception validation function, returns `Exception, None, expected_e`.

**Parameters:**

 - `expected_e`: an `ExpectedError`, that is, either an exception type, an exception instance, or an exception validation function


### `get_all_cases`

`get_all_cases(cases=None, module=None, this_module_object=None, has_tag=None, filter=None) -> List[CaseDataGetter]`

Lists all desired cases for a given user query. This function may be convenient for debugging purposes.
    

**Parameters:**

 - `cases`: a single case or a hardcoded list of cases to use. Only one of `cases` and `module` should be set.
 - `module`: a module or a hardcoded list of modules to use. You may use `THIS_MODULE` to indicate that the module is the current one. Only one of `cases` and `module` should be set.
 - `this_module_object`: any variable defined in the module of interest, for example a function. It is used to find "this module", when `module` contains `THIS_MODULE`. 
 - `has_tag`: an optional tag used to filter the cases in the `module`. Only cases with the given tag will be selected.
 - `filter`: an optional filtering function taking as an input a list of tags associated with a case, and returning a boolean indicating if the case should be selected. It will be used to filter the cases in the `module`. It both `has_tag` and `filter` are set, both will be applied in sequence.
