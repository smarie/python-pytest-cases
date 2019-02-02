# Advanced usage

## Case arguments

Case functions can have arguments. This makes it very easy to combine test cases with more elaborate pytest concepts (fixtures, parameters):

```python
import pytest
from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE

def case_simple(version: str) -> CaseData:
    print("using version " + version)
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None

def case_simple2(version: str) -> CaseData:
    print("using version " + version)
    ins = dict(a=1, b=2)
    outs = 2, 3
    return ins, outs, None

# the order of the loops will be [for version] > [for case]
@cases_data(module=THIS_MODULE)
@pytest.mark.parametrize("version", ["1.0.0", "2.0.0"])
def test_with_parameters(case_data: CaseDataGetter, version):
    # 1- Grab the test case data with the parameter
    i, expected_o, expected_e = case_data.get(version)
    
    # 2- Use it as usual...
    # ...
```

This also works with case generators: simply add the argument(s) to the function signature, *without* declaring them in the `@cases_generator` decorator.

```python
@cases_generator("gen case i={i}, j={j}", i=range(2), j=range(2))
def case_gen(version: str, i: int, j: int) -> CaseData:
    print("using version " + version)
    ins = dict(a=i, b=j)
    outs = i+1, j+1
    return ins, outs, None
```


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

### With variants

If the tests use the same shared cases but with small differences, you may wish to add [arguments](#case_arguments) to your case functions.

### Caching

After starting to reuse cases in several test functions, you might end-up thinking *"why do I have to spend the data parsing/generation time several times ? It is the same case."*. You can solve this issue by using a cache.

For simple cases you can simply decorate your case function with `@lru_cache(maxsize=1)` since simple case functions do not have arguments:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def case_a():
    # ... (as usual)
```

For case generators you **can** also use `@lru_cache(maxsize=x)`, but you will have to set the max size according to the number of generated cases (or `None` to allow auto-grow). This can be automated: simply use the `lru_cache=True` parameter and `pytest-cases` will do it for you:

```python
from pytest_cases import CaseData, cases_data, CaseDataGetter, THIS_MODULE, \
  cases_generator

# ----------------------CASES--------------------------
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
    ...


@cases_data(module=THIS_MODULE)
def test_b(case_data: CaseDataGetter):
    # 1- Grab the test case data
    i, expected_o, expected_e = case_data.get()

    # 2- Use it
    ...
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

**WARNING** if you use [case arguments](#case_arguments), do not forget to take the additional parameter values into account to estimate the total cache size. Note that the `lru_cache=` option of `@cases_generator` is not intelligent enough to handle additional arguments: do not use it, and instead manually apply the `@lru_cache` decorator.


## Incremental tests with [pytest-steps](https://smarie.github.io/python-pytest-steps/)

Sometimes you wish to execute a series of test steps on the same dataset, and then to move to another one. There are many ways to do this with `pytest` but some of them are not easy to blend with the notion of 'cases' in an intuitive manner. `pytest-cases` is compliant with [pytest-steps](https://smarie.github.io/python-pytest-steps/): you can easily create incremental tests and throw your cases on them.

This tutorial assumes that you are already familiar with [pytest-steps](https://smarie.github.io/python-pytest-steps/).


### 1- If steps can run with the same data

If all of the test steps require the same data to execute, it is straightforward, both in parametrizer mode (shown below) or in the new pytest steps generator mode (not shown):


```python
from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, CaseData
from pytest_steps import test_steps

# -------- test cases
def case_simple() -> CaseData:
    ins = dict(a=1, b=2)
    return ins, None, None

def case_simple2() -> CaseData:
    ins = dict(a=-1, b=2)
    return ins, None, None

# ------- test steps
def step_a(steps_data, ins, expected_o, expected_e):
    """ Step a of the test """
    # Use the three items as usual
    ...
    # You can also store intermediate results in steps_data

def step_b(steps_data, ins, expected_o, expected_e):
    """ Step b of the test """
    # Use the three items as usual
    ...
    # You can also retrieve intermediate results from steps_data

# ------- test suite
@test_steps(step_a, step_b)
@cases_data(module=THIS_MODULE)
def test_suite(test_step, case_data: CaseDataGetter, steps_data):
    # Get the data for this step
    ins, expected_o, expected_e = case_data.get()

    # Execute the step
    test_step(steps_data, ins, expected_o, expected_e)
```

This yields:

```bash
============================= test session starts =============================
...
test_p.py::test_suite[case_simple-step_a] PASSED  [ 25%]{'a': 1, 'b': 2}
test_p.py::test_suite[case_simple-step_b] PASSED  [ 50%]{'a': 1, 'b': 2}
test_p.py::test_suite[case_simple2-step_a] PASSED [ 75%]{'a': -1, 'b': 2}
test_p.py::test_suite[case_simple2-step_b] PASSED [100%]{'a': -1, 'b': 2}
========================== 4 passed in 0.13 seconds ===========================
```

You see that for each case data, all steps are executed in order. If you use an IDE it will appear in this intuitive order too:

```bash
case_simple
 - step_a
 - step_b
case_simple2
 - step_a
 - step_b
``` 

If for some reason you wish to invert the order (executing all cases on step a then all cases on step b etc.) simply invert the order of decorators and it will work (`pytest` is great!). This is not recommended though, as it is a lot less intuitive.

Of course you might want to [enable caching](#caching) so that the cases will be read only once, and not once for each test step.

### 2- If steps require different data (A: dicts)

In real-world usage, each step will probably have different expected output or errors for the same case - except if the steps are very similar. The steps may even need slightly different input, for example the same dataset but in two different formats.

This is actually quite straightforward: simply adapt your custom case data format definition! Since `pytest-cases` does not impose **any** format for your case functions outputs, you can decide that your case functions return lists, dictionaries, etc.

For example you can choose the format proposed by the `MultipleStepsCaseData` type hint, where each item in the returned inputs/outputs/errors tuple can either be a single element, or a dictionary of name -> element. This allows your case functions to return alternate contents depending on the test step being executed.

The example below shows a test suite where the inputs of the steps are the same, but the outputs and expected errors are different. Note that once again the example relies on the legacy "parametrizer" mode of pytest-steps, but it would be similar with the new "generator" mode.

```python
from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, \
  MultipleStepsCaseData
from pytest_steps import test_steps

# -------- test cases
def case_simple() -> MultipleStepsCaseData:
    # common input
    ins = dict(a=1, b=2)
    
    # one expected output for each step
    outs_for_a = 2, 3
    outs_for_b = 5, 4
    outs = dict(step_check_a=outs_for_a, step_check_b=outs_for_b)

    return ins, outs, None

def case_simple2() -> MultipleStepsCaseData:
    # common input
    ins = dict(a=-1, b=2)

    # one expected output for each step
    outs_for_a = 2, 3
    outs_for_b = 5, 4
    outs = dict(step_check_a=outs_for_a, step_check_b=outs_for_b)

    return ins, outs, None

# ------- test steps
def step_check_a(steps_data, ins, expected_o, expected_e):
    """ Step a of the test """
    # Use the three items as usual
    ...
    # You can also store intermediate results in steps_data

def step_check_b(steps_data, ins, expected_o, expected_e):
    """ Step b of the test """
    # Use the three items as usual
    ...
    # You can also retrieve intermediate results from steps_data

# ------- test suite
@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite(test_step, case_data: CaseDataGetter, steps_data):
    # Get the case data for all steps (sad...)
    ins, expected_o, expected_e = case_data.get()

    # Filter it, based on the step name
    key = test_step.__name__
    expected_o = None if expected_o is None else expected_o[key]
    expected_e = None if expected_e is None else expected_e[key]

    # Execute the step
    test_step(steps_data, ins, expected_o, expected_e)
```

There are two main differences with the previous example:

 - in the `case_simple` and `case_simple2` case functions, we choose to provide the expected output and expected error as **dictionaries indexed by the test step name** when they are non-`None`. We also choose that the input is the same for all steps, but we could have done otherwise - using a dictionary with step name keys as well.
 - in the final `test_suite` we use the test step name dictionary key to get the case data contents **for a given step**.

Once again you might want to [enable caching](#caching) in order for the cases to be read only once, and not once for each test step.

### 3- If steps require different data (B: arguments, recommended)

The above example might seem a bit disappointing as it breaks the philosophy of doing each data access **only when it is needed**. Indeed everytime a single step is run it actually gets the data for all steps and then has to do some filtering.

The style suggested below, making use of [case arguments](./advanced#case_arguments), is probably better: 

```python
from pytest_cases import cases_data, CaseDataGetter, THIS_MODULE, CaseData
from pytest_steps import test_steps

# -------- test cases
def case_simple(step_name: str) -> CaseData:
    # reuse the same input whatever the step
    ins = dict(a=1, b=2)
    
    # adapt the expected output to the current step
    if step_name is 'step_check_a':
        outs = 2, 3
    elif step_name is 'step_check_b':
        outs = 5, 4

    return ins, outs, None

def case_simple2(step_name: str) -> CaseData:
    # reuse the same input whatever the step
    ins = dict(a=-1, b=2)

    # adapt the expected output to the current step
    if step_name is 'step_check_a':
        outs = 0, 3
    elif step_name is 'step_check_b':
        outs = 1, 4

    return ins, outs, None

# ------- test steps
def step_check_a(steps_data, ins, expected_o, expected_e):
    """ Step a of the test """
    # Use the three items as usual
    ...
    # You can also store intermediate results in steps_data

def step_check_b(steps_data, ins, expected_o, expected_e):
    """ Step b of the test """
    # Use the three items as usual
    ...
    # You can also retrieve intermediate results from steps_data

# ------- test suite
@test_steps(step_check_a, step_check_b)
@cases_data(module=THIS_MODULE)
def test_suite(test_step, case_data: CaseDataGetter, steps_data):

    # Get the data for this particular case
    ins, expected_o, expected_e = case_data.get(test_step.__name__)

    # Execute the step
    test_step(steps_data, ins, expected_o, expected_e)
```

Notice that now **the test step name is a parameter of the case function**. So for each step, only the data relevant to this step is retrieved. 

Once again you might want to enable caching in order for the cases to be read only once, and not once for each test step. However since the case functions now have arguments, you should **not** use `@lru_cache()` directly on the case function but you should put it in a separate subfunction:

```python
from pytest_cases import CaseData
from functools import lru_cache

@lru_cache()
def input_for_case_simple():
    return dict(a=1, b=2)

def case_simple(step_name: str) -> CaseData:
    # reuse the same input whatever the step
    ins = input_for_case_simple()
    
    # adapt the expected output to the current step
    if step_name is 'step_check_a':
        outs = 2, 3
    elif step_name is 'step_check_b':
        outs = 5, 4

    return ins, outs, None
```

That way, `input_for_case_simple` will be cached across the steps.

See [caching](#caching) for details.


## Advanced Pytest: Manual parametrization

The `@cases_data` decorator is just syntactic sugar for the following two-steps process, that you may wish to rely on for advanced pytest usages:

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
@pytest.mark.parametrize('case_data', marked_cases, ids=cases_ids)
def test_with_cases_decorated(case_data):
    ...
```
