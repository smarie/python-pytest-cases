# Changelog

### 1.5.0 - new helpers `param_fixture` and `param_fixtures`

Following [Sup3rGeo](https://github.com/Sup3rGeo)'s proposal, introduced two helper methods to create simple "parameter fixtures". Fixes [#31](https://github.com/smarie/python-pytest-cases/issues/31)

### 1.4.2 - parametrized `@pytest_fixture_plus` minor bug fix

`@pytest_fixture_plus` now correctly honors parameter id and marks overriden at single parameter level using `pytest.param`. Fixed [#30](https://github.com/smarie/python-pytest-cases/issues/30)

### 1.4.1 - parametrized `@pytest_fixture_plus` minor bug fix

Fixed `@pytest_fixture_plus` in case it is used with `parametrize` and one parameter is itself customized using `pytest.param`. Fixed [#29](https://github.com/smarie/python-pytest-cases/issues/29).

### 1.4.0 - `@pytest_fixture_plus` major improvement

 * Major improvement of `@pytest_fixture_plus`: instead of generating fixtures, it now correctly parametrizes the fixture. Skip/fail Marks are correctly copied too. Fixes [#28](https://github.com/smarie/python-pytest-cases/issues/28)

 * `pytest_fixture_plus` does not accept the `params` and `ids` arguments any more, it only relies on parametrization marks.

### 1.3.3 - parametrized `@pytest_fixture_plus` Bugfix

Fixed minor bug with parametrized `@pytest_fixture_plus`: spaces are now correctly removed when multiple parameter names are provided in the same `parametrize` call. Fixes [#27](https://github.com/smarie/python-pytest-cases/issues/27)

### 1.3.2 - parametrized `@pytest_fixture_plus` Bugfix

Fixed bug with `@pytest_fixture_plus` when used in parametrized mode. Fixes [#26](https://github.com/smarie/python-pytest-cases/issues/26). Thanks [Sup3rGeo](https://github.com/Sup3rGeo)!

### 1.3.1 - Minor dependency change

Now using `decopatch` to create the decorators.

### 1.3.0 - More flexible case generators names + Minor dependency change

Cases generators can now support explicit name lists, and name generator callables, in addition to the name template strings. Fixed [#24](https://github.com/smarie/python-pytest-cases/issues/24)

Dependency to `decorator` has been dropped and replaced with `makefun`. Fixed [#25](https://github.com/smarie/python-pytest-cases/issues/25).

### 1.2.2 - fixed bug with marks on cases with pytest 3.3

Marks on cases are now also working with pytest 3.3. Fixed [#23](https://github.com/smarie/python-pytest-cases/issues/23)

Ids for marked tests are now better managed. A new function `get_pytest_parametrize_args` is now used to transform the list of cases obtained by `get_all_cases(module)`, into the list of marked cases and ids required by `@pytest.mark.parametrize`. The doc has been updated to explain this for advanced users wishing to perform this step manually.

### 1.2.1 - fixed id of test cases with marks

Id of test cases with marks was appearing as `ParameterSet`. Fixed it.

### 1.2.0 - @pytest.mark can be used on cases + @pytest_fixture_plus parametrization order bugfix

Pytest marks such as `@pytest.mark.skipif` can now be used on case functions. As a consequence, `get_all_cases` is now the recommended function to use instead of `extract_cases_from_module` to perform manual collection. Indeed `get_all_cases` correctly prepares the resulting parameters list so that pytest sees the marks. Fixed [#21](https://github.com/smarie/python-pytest-cases/issues/21) 

Fixed parametrization order when `@pytest_fixture_plus` is used with several `@pytest.mark.parametrize`. Fixed [#22](https://github.com/smarie/python-pytest-cases/issues/22).

### 1.1.1 - Improved generated fixture names for `@pytest_fixture_plus`

When `@pytest_fixture_plus` is used on a function marked as parametrized, some fixtures are generated (one for each parameter). Generated fixture names now follow the pattern `<fixturename>__<paramname>`.
Fixed [#20](https://github.com/smarie/python-pytest-cases/issues/20).

### 1.1.0 - New `@pytest_fixture_plus`

New decorator `@pytest_fixture_plus` allows to use several `@pytest.mark.parametrize` on a fixture. Therefore one can use multiple `@cases_data` decorators, too. Fixes [#19](https://github.com/smarie/python-pytest-cases/issues/19).
*Note: this is a temporary feature, that will be removed if/when [pytest supports it](https://github.com/pytest-dev/pytest/issues/3960).*

### 1.0.0 - `@cases_fixture` + pytest 2.x support 

Pytest 2.x is now supported. Fixes [#14](https://github.com/smarie/python-pytest-cases/issues/14)

**New feature:** `@cases_fixture` ! Now you can put your cases data retrieval in a fixture so that its duration does not enter into the test duration. This is particularly interesting if you use [pytest-harvest](https://smarie.github.io/python-pytest-harvest/) to create benchmarks: you probably do not want the case data retrieval/parsing to be counted in the test duration, especially if you use caching on the case function to accelerate subsequent retrievals. Fixes [#15](https://github.com/smarie/python-pytest-cases/issues/15)

### 0.10.1 - minor encoding issue in setup.py

### 0.10.0 - support for python 2

Python 2 is now supported. Fixed [#3](https://github.com/smarie/python-pytest-cases/issues/3) 

 - Note: `CaseData`, `Given`, `ExpectedNormal`, `ExpectedError`, and `MultipleStepsCaseData` type hints is not created in python 2 and python<3.5

### 0.9.1 - pytest-steps is now an independent project

 * Light refactoring: some internal function names are now private, and there are now two submodules.
 * [pytest-steps](https://smarie.github.io/python-pytest-steps/) is now an independent project. Examples in the documentation have been updated
 * New documentation page: API reference

### 0.8.0 - Filtering can now be done using a callable.

 * `@cases_data`: the `filter` argument now contains a filtering function. WARNING: the previous behaviour is still available but has been renamed `has_tag`. Fixes [#8](https://github.com/smarie/python-pytest-cases/issues/8)

### 0.7.0 - Hardcoded cases selection, and multi-module selection

 * `@cases_data` has a new parameters `cases` that can be used to hardcode a case or a list of cases. Its `module` parameter can also now take a list of modules

### 0.6.0 - Case parameters and better test suites

 * `get_for` is deprecated: it was too specific to a given case data format.
 * `MultipleStepsCaseData` was fixed to also support multiple inputs.
 * Case functions can now have parameters (even case generators). This is particularly useful for test suites. Fixes [#9](https://github.com/smarie/python-pytest-cases/issues/9)

### 0.5.0 - support for test suites

 * test functions can now be decorated with `@test_steps` to easily define a test suite with several steps. This fixes [#7](https://github.com/smarie/python-pytest-cases/issues/7)

### 0.4.0 - support for data caching with lru_cache

 * cases can now be decorated with `@lru_cache`. `@cases_generator` also provides a `lru_cache` parameter to enable caching. Fixes [#6](https://github.com/smarie/python-pytest-cases/issues/6)

### 0.3.0 - case generators

 * New decorator `@cases_generator` to define case generators. Fixes [#1](https://github.com/smarie/python-pytest-cases/issues/1)
 * Also, removed unused functions `is_expected_error_instance` and `assert_exception_equal`

### 0.2.0 - THIS_MODULE constant + Tagging/Filtering + doc

 * New constant `THIS_MODULE` so that cases and test functions can coexist in the same file. This fixes [#5](https://github.com/smarie/python-pytest-cases/issues/5)

 * Added `@test_target` and `@case_tags` decorators for case functions, and added `filter` parameter in `@cases_data`. This allows users to :
 
     * tag a case function with any item (and in particular with the reference to the function it relates to), 
     * and to filter the case functions used by a test function according to a particular tag.

   This fixes [#4](https://github.com/smarie/python-pytest-cases/issues/4)

 * Improved documentation

### 0.1.0 - First public version

 * Initial fork from private repo
