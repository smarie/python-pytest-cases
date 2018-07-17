# Advanced usage

## Case parameters

Case functions can have parameters. This makes it very easy to combine test cases with more elaborate pytest concepts (fixtures, parameters):

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

This also works with case generators: simply add the parameter(s) to the function signature, without declaring them in the `@cases_generator` decorator.

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

If the tests use the same shared cases but with small differences, you may wish to add [parameters](#case_parameters) to your case functions.

### Caching

After starting to reuse cases in several test functions, you might end-up thinking *"why do I have to spend the data parsing/generation time several times ? It is the same case."*. You can solve this issue by using a cache.

For simple cases you can simply decorate your case function with `@lru_cache(maxsize=1)` since simple case functions do not have parameters:

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

**WARNING** if you use [case parameters](#case_parameters), do not forget to take the additional parameter values into account to estimate the total cache size. Note that the `lru_cache=` option of `@cases_generator` is not intelligent enough to handle additional parameters: do not use it, and instead manually apply the `@lru_cache` decorator.

## Test "suites": several steps on each case 

Sometimes you wish to execute a series of tests on the same dataset, and then to move to another one. This is feasible with `pytest_cases`.

### 0- The `@test_steps` decorator

This decorator can be used independently from the rest of this package. It is simply a convenient and readable specialization of `@pytest.mark.parametrize` so as to breakdown a test into sub-steps. To use it, simply:

 - create several step functions, e.g. `step_check_a`, `step_check_b`...
 - create a test function representing the "suite", and decorate it with `@test_steps`
 - fill the function so as to retrieve the appropriate data in each step. It can be done within the function body as shown below, or thanks to additional `parametrize` decorators.

```python
from pytest_cases import test_steps

# ------- test steps
def step_check_a(inputs, expected_o, expected_e):
    """ Step a of the test """
    print(inputs)

def step_check_b(inputs, expected_o, expected_e):
    """ Step b of the test """
    print(inputs)

# ------- test suite
@test_steps(step_check_a, step_check_b)
def test_suite(test_step):
    # Get the data for this step
    inputs, expected_o, expected_e = todo_get_data_for_step(test_step)

    # Execute the step
    test_step(inputs, expected_o, expected_e)
```


### a- Identical cases for all

It is very easy to make all test steps use the same identical cases data:

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
test_p.py::test_suite[case_simple-step_check_a] PASSED  [ 25%]{'a': 1, 'b': 2}
test_p.py::test_suite[case_simple-step_check_b] PASSED  [ 50%]{'a': 1, 'b': 2}
test_p.py::test_suite[case_simple2-step_check_a] PASSED [ 75%]{'a': -1, 'b': 2}
test_p.py::test_suite[case_simple2-step_check_b] PASSED [100%]{'a': -1, 'b': 2}
========================== 4 passed in 0.13 seconds ===========================
```

You see that for each case data, all steps are executed in order. You can wish (more rarely) to invert the order, executing all cases on step a then all cases on step b etc. Simply invert the order of decorators and it will work (`pytest` is great!).

Of course you might want to [enable caching](#caching) so that the cases will be read only once, and not once for each test step.

### b- Per-step Case variants v0.5

What if each step requires different expected output or errors for the same case ? Or even slightly different inputs ? Simply adapt your case data format definition! Since `pytest-cases` does not impose **any** format for your case functions outputs, you can decide to return lists, dictionaries, etc.

If you wish to start with something, you can choose the format proposed by `MultipleStepsCaseData`, where each item in the tuple (the inputs, outputs and error) can either be a single element, or a dictionary of name -> element. This allows you to store alternate contents whenever your test steps require it.

The example below shows a test suite where the inputs of the steps are the same, but the outputs and expected errors are different:

```python
from pytest_cases import test_steps, cases_data, CaseDataGetter, THIS_MODULE, \
 MultipleStepsCaseData

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
    # Get the case data for all steps (sad...)
    ins, expected_o, expected_e = case_data.get()

    # Filter it, based on the step name
    key = test_step.__name__
    expected_o = None if expected_o is None else expected_o[key]
    expected_e = None if expected_e is None else expected_e[key]

    # Execute the step
    test_step(ins, expected_o, expected_e)
```

There are two main differences with the first version:

 - in the `case_simple` and `case_simple2` case functions, we choose to provide the expected output and expected error as dictionaries when they are non-`None`, where the key is the step name. We also choose that the input is the same for all steps, but we could have done otherwise using a dictionary with step name keys as well.
 - in the final `test_suite` we use the step name to filter the case data contents **for a given step**

Once again you might want to [enable caching](#caching) in order for the cases to be read only once, and not once for each test step.

### c- Per-step Case variants v1

The above example might seem a bit disappointing as it breaks the philosophy of doing each data access **only when it is needed**. Indeed everytime a single step is run it actually gets the data for all steps and then has to do some filtering.

The style suggested below, making use of [case parameters](./advanced#case_parameters) is probably better: 

```python
from pytest_cases import test_steps, cases_data, CaseDataGetter, THIS_MODULE, \
  CaseData

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

    # Get the data for this particular case
    ins, expected_o, expected_e = case_data.get(test_step.__name__)

    # Execute the step
    test_step(ins, expected_o, expected_e)
```

Notice that now **the test step name is a parameter of the case function**. So for each step, only the data relevant to this step is retrieved. Of course if there are common parts across the steps for the same case, you can still put them in a shared function with `@lru_cache` enabled:

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

See [caching](#caching) for details


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
