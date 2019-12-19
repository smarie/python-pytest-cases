# Changelog

### 1.12.0 - better test ids for parametrized tests with fixture refs + bugfix

 - Improved test ids for the cases where `fixture_ref` is used in the parameters list in `@pytest_parametrize_plus`. Fixed [#69](https://github.com/smarie/python-pytest-cases/issues/69). Thanks [`last-partizan`](https://github.com/last-partizan) for the suggestion !

 - Fixed `TypeError: got an unexpected keyword argument 'indirect'` with `pytest` 5+. Fixed [#70](https://github.com/smarie/python-pytest-cases/issues/70).

### 1.11.9 - bugfix

`FixtureClosureNode` is now able to properly handle `ignore_args`, and now supports that plugins append fixtures to the closure, such as pytest-asyncio. Added corresponding tests. Fixes [#68](https://github.com/smarie/python-pytest-cases/issues/68)

### 1.11.8 - bugfix

Fixed `KeyError` issue happening when a fixture is not found. Now users will see the "normal" error message from pytest (`"fixture <name> not found"`). Fixed [#67](https://github.com/smarie/python-pytest-cases/issues/67).

### 1.11.7 - bugfix

Fixed `ValueError` issue happening with indirectly parametrized fixtures. Fixed [#64](https://github.com/smarie/python-pytest-cases/issues/64).

### 1.11.6 - pyproject.toml

[raddessi](https://github.com/raddessi) added a `pyproject.toml` - thanks! Fixed [#65](https://github.com/smarie/python-pytest-cases/issues/65).

### 1.11.5 - bugfix

`pytest_parametrize_plus` was not working correctly with test classes, leading to `fixture 'self' not found`. Fixed [#63](https://github.com/smarie/python-pytest-cases/issues/63).

### 1.11.4 - python 2 bugfix

Fixed issue happening with `@pytest.mark.parametrize` with python 2. Fixed [#62](https://github.com/smarie/python-pytest-cases/issues/62).

### 1.11.3 - minor improvements

Better error message when users use `THIS_MODULE` in `cases=` instead of `module=`.

Added `__version__` package-level attribute.

### 1.11.2 - Increased tolerance to other plugins + bugfix

Now when other plugins try to manipulate the fixture closure, warning messages are emitted but no error is raised. Fixed [#55](https://github.com/smarie/python-pytest-cases/issues/55).

Also fixed issue [#58](https://github.com/smarie/python-pytest-cases/issues/58) happening with doctest.

### 1.11.1 - Added `six` dependency explicitly

It was missing from `setup.py`.

### 1.11.0 - `fixture_ref` can now be used inside tuples, leading to cross-products

Fixes [#47](https://github.com/smarie/python-pytest-cases/issues/47).

### 1.10.2 - More intuitive error messages

Now raising an explicit `InvalidParamsList` when pytest parametrize `argvalues` are incorrect. See [#54](https://github.com/smarie/python-pytest-cases/issues/54)

### 1.10.1 - Bugfix

Fixed [#52](https://github.com/smarie/python-pytest-cases/issues/52).

### 1.10.0 - New feature: fixtures unpacking

You can now unpack a fixture iterable into several individual fixtures using `unpack_fixture` or using `@pytest_fixture_plus(unpack_into=<names>)`. This is also available in `union_fixture(unpack_into=<names>)`. Fixed [#50](https://github.com/smarie/python-pytest-cases/issues/50) and [#51](https://github.com/smarie/python-pytest-cases/issues/51).

### 1.9.3 - Bugfix

Fixed issues when parametrize argnames contains a list. This fixed [#49](https://github.com/smarie/python-pytest-cases/issues/49)

### 1.9.2 - Bugfix with pytest 3.7 

Fixed [#48](https://github.com/smarie/python-pytest-cases/issues/48).

### 1.9.1 - Bugfix with pytest 3.7

Fixed [#48](https://github.com/smarie/python-pytest-cases/issues/48).

### 1.9.0 - New `--with-reorder` commandline option

New commandline option '--with-reorder' to change the reordering startegy currently in application. Fixes [#45](https://github.com/smarie/python-pytest-cases/issues/45).

The `--with-reorder` "skip" mode was not working correctly in presence of marks, fixed it. Fixed [#46](https://github.com/smarie/python-pytest-cases/issues/46).

### 1.8.1 - BugFixes

Ids should not be used when setting a NOT_USED parametrization. Fixes [#43](https://github.com/smarie/python-pytest-cases/issues/43)

Fixed issue with ordering and setup/teardown for higher-level scope fixtures (session and module scopes) when using union fixtures. Fixes [#44](https://github.com/smarie/python-pytest-cases/issues/44)

### 1.8.0 - Better ids for fixture unions

New:

 - `fixture_union` now accept a non-`None` value for `ids`. It also has a new `idstyle` argument allowing users to change the style of ids used. Finally `pytest_parametrize_plus` relies on this `ids` argument to set a more readable list of ids for the created union. Fixes [#41](https://github.com/smarie/python-pytest-cases/issues/41).

Misc:

 - Added non-regression test for fixture order. It passes already for all recent pytest versions (after 3.3). Fixes [#42](https://github.com/smarie/python-pytest-cases/issues/42)

### 1.7.0 - New `@pytest_parametrize_plus` allowing fixture references to be used in parameter values

New decorator `@pytest_parametrize_plus` able to handle the case where a `fixture_ref(<fixture_name>)` is present in the parameter values list. This decorator can be applied both on test functions and fixtures (if they are decorated with `@pytest_fixture_plus`). Fixes [#40](https://github.com/smarie/python-pytest-cases/issues/40)

Major refactoring of the "union fixtures" mechanism.

 - The `NOT_USED` status is now correctly propagated between dependent fixtures. This should fix a few cases where user fixtures were setup/teardown while not used in the current test node.
 - Empty fixture unions are not permitted anymore.
 - The way unions are handled in test parametrization was redesigned. The new design is based on a two-steps approach: first build the fixture closure for each node as a tree (and not a list as in `pytest`), and then apply parametrization intelligently based on this tree structure. This fixes several unintuitive behaviours that were happening with unions.

Note: interestingly this also fixes [pytest#5054](https://github.com/pytest-dev/pytest/issues/5054).

### 1.6.3 - Minor exception enhancement

Improved the error message when the name template is wrong in `@cases_generator`. Fixes [#39](https://github.com/smarie/python-pytest-cases/issues/39).

### 1.6.2 - bug fixes

`fixture_union`:

 * Changed the repr of `NOT_USED` to `pytest_cases.NOT_USED`.

 * `@pytest_fixture_plus` now correctly handles the `NOT_USED` when fixtures in the union do not contain any parameter. Fixes [#38](https://github.com/smarie/python-pytest-cases/issues/38).

`param_fixtures`:

 * `param_fixtures` now delegates to `param_fixture` when a single parameter name is provided. This is more consistent. Fixed [#36](https://github.com/smarie/python-pytest-cases/issues/36).

 * `param_fixture[s]` now support all arguments from `fixture` (`scope` and `autouse` in particular).

### 1.6.1 - `@pytest_fixture_plus` improvement to handle `NOT_USED` cases

Fixed issue where fixtures get called with `NOT_USED` as a parameter when using a `fixture_union`. This issue is actually only fixed in `@pytest_fixture_plus`, if you use `@pytest.fixture` you have to handle it manually. Fixes [#37](https://github.com/smarie/python-pytest-cases/issues/37).

### 1.6.0 - `fixture_union` and `param_fixture[s]` bugfix

New `fixture_union` method to create a fixture that is the union/combination of other fixtures. This is an attempt to solve [this pytest proposal](https://docs.pytest.org/en/latest/proposals/parametrize_with_fixtures.html).

Also, `param_fixture` and `param_fixtures` can now be used without necessarily storing the return value into a variable: they will automatically register the created fixtures in the calling module.  

Finally, fixed a bug with `param_fixtures` when called to create a fixture for a single parameter.

### 1.5.1 - `param_fixtures` bugfix

Fixed `param_fixtures` issue: all parameter values were identical to the last parameter of the tuple. Fixes [#32](https://github.com/smarie/python-pytest-cases/issues/32).

### 1.5.0 - new helpers `param_fixture` and `param_fixtures`

Following [Sup3rGeo](https://github.com/Sup3rGeo)'s proposal, introduced two helper methods to create simple "parameter fixtures". Fixes [#31](https://github.com/smarie/python-pytest-cases/issues/31).

### 1.4.2 - parametrized `@pytest_fixture_plus` minor bug fix

`@pytest_fixture_plus` now correctly honors parameter id and marks overriden at single parameter level using `pytest.param`. Fixed [#30](https://github.com/smarie/python-pytest-cases/issues/30).

### 1.4.1 - parametrized `@pytest_fixture_plus` minor bug fix

Fixed `@pytest_fixture_plus` in case it is used with `parametrize` and one parameter is itself customized using `pytest.param`. Fixed [#29](https://github.com/smarie/python-pytest-cases/issues/29).

### 1.4.0 - `@pytest_fixture_plus` major improvement

 * Major improvement of `@pytest_fixture_plus`: instead of generating fixtures, it now correctly parametrizes the fixture. Skip/fail Marks are correctly copied too. Fixes [#28](https://github.com/smarie/python-pytest-cases/issues/28).

 * `pytest_fixture_plus` does not accept the `params` and `ids` arguments any more, it only relies on parametrization marks.

### 1.3.3 - parametrized `@pytest_fixture_plus` Bugfix

Fixed minor bug with parametrized `@pytest_fixture_plus`: spaces are now correctly removed when multiple parameter names are provided in the same `parametrize` call. Fixes [#27](https://github.com/smarie/python-pytest-cases/issues/27).

### 1.3.2 - parametrized `@pytest_fixture_plus` Bugfix

Fixed bug with `@pytest_fixture_plus` when used in parametrized mode. Fixes [#26](https://github.com/smarie/python-pytest-cases/issues/26). Thanks [Sup3rGeo](https://github.com/Sup3rGeo)!

### 1.3.1 - Minor dependency change

Now using `decopatch` to create the decorators.

### 1.3.0 - More flexible case generators names + Minor dependency change

Cases generators can now support explicit name lists, and name generator callables, in addition to the name template strings. Fixed [#24](https://github.com/smarie/python-pytest-cases/issues/24).

Dependency to `decorator` has been dropped and replaced with `makefun`. Fixed [#25](https://github.com/smarie/python-pytest-cases/issues/25).

### 1.2.2 - fixed bug with marks on cases with pytest 3.3

Marks on cases are now also working with pytest 3.3. Fixed [#23](https://github.com/smarie/python-pytest-cases/issues/23).

Ids for marked tests are now better managed. A new function `get_pytest_parametrize_args` is now used to transform the list of cases obtained by `get_all_cases(module)`, into the list of marked cases and ids required by `@pytest.mark.parametrize`. The doc has been updated to explain this for advanced users wishing to perform this step manually.

### 1.2.1 - fixed id of test cases with marks

Id of test cases with marks was appearing as `ParameterSet`. Fixed it.

### 1.2.0 - @pytest.mark can be used on cases + @pytest_fixture_plus parametrization order bugfix

Pytest marks such as `@pytest.mark.skipif` can now be used on case functions. As a consequence, `get_all_cases` is now the recommended function to use instead of `extract_cases_from_module` to perform manual collection. Indeed `get_all_cases` correctly prepares the resulting parameters list so that pytest sees the marks. Fixed [#21](https://github.com/smarie/python-pytest-cases/issues/21). 

Fixed parametrization order when `@pytest_fixture_plus` is used with several `@pytest.mark.parametrize`. Fixed [#22](https://github.com/smarie/python-pytest-cases/issues/22).

### 1.1.1 - Improved generated fixture names for `@pytest_fixture_plus`

When `@pytest_fixture_plus` is used on a function marked as parametrized, some fixtures are generated (one for each parameter). Generated fixture names now follow the pattern `<fixturename>__<paramname>`.
Fixed [#20](https://github.com/smarie/python-pytest-cases/issues/20).

### 1.1.0 - New `@pytest_fixture_plus`

New decorator `@pytest_fixture_plus` allows to use several `@pytest.mark.parametrize` on a fixture. Therefore one can use multiple `@cases_data` decorators, too. Fixes [#19](https://github.com/smarie/python-pytest-cases/issues/19).
*Note: this is a temporary feature, that will be removed if/when [pytest supports it](https://github.com/pytest-dev/pytest/issues/3960).*

### 1.0.0 - `@cases_fixture` + pytest 2.x support 

Pytest 2.x is now supported. Fixes [#14](https://github.com/smarie/python-pytest-cases/issues/14).

**New feature:** `@cases_fixture` ! Now you can put your cases data retrieval in a fixture so that its duration does not enter into the test duration. This is particularly interesting if you use [pytest-harvest](https://smarie.github.io/python-pytest-harvest/) to create benchmarks: you probably do not want the case data retrieval/parsing to be counted in the test duration, especially if you use caching on the case function to accelerate subsequent retrievals. Fixes [#15](https://github.com/smarie/python-pytest-cases/issues/15).

### 0.10.1 - minor encoding issue in setup.py

### 0.10.0 - support for python 2

Python 2 is now supported. Fixed [#3](https://github.com/smarie/python-pytest-cases/issues/3). 

 - Note: `CaseData`, `Given`, `ExpectedNormal`, `ExpectedError`, and `MultipleStepsCaseData` type hints is not created in python 2 and python<3.5

### 0.9.1 - pytest-steps is now an independent project

 * Light refactoring: some internal function names are now private, and there are now two submodules.
 * [pytest-steps](https://smarie.github.io/python-pytest-steps/) is now an independent project. Examples in the documentation have been updated
 * New documentation page: API reference

### 0.8.0 - Filtering can now be done using a callable.

 * `@cases_data`: the `filter` argument now contains a filtering function. WARNING: the previous behaviour is still available but has been renamed `has_tag`. Fixes [#8](https://github.com/smarie/python-pytest-cases/issues/8).

### 0.7.0 - Hardcoded cases selection, and multi-module selection

 * `@cases_data` has a new parameters `cases` that can be used to hardcode a case or a list of cases. Its `module` parameter can also now take a list of modules

### 0.6.0 - Case parameters and better test suites

 * `get_for` is deprecated: it was too specific to a given case data format.
 * `MultipleStepsCaseData` was fixed to also support multiple inputs.
 * Case functions can now have parameters (even case generators). This is particularly useful for test suites. Fixes [#9](https://github.com/smarie/python-pytest-cases/issues/9).

### 0.5.0 - support for test suites

 * test functions can now be decorated with `@test_steps` to easily define a test suite with several steps. This fixes [#7](https://github.com/smarie/python-pytest-cases/issues/7).

### 0.4.0 - support for data caching with lru_cache

 * cases can now be decorated with `@lru_cache`. `@cases_generator` also provides a `lru_cache` parameter to enable caching. Fixes [#6](https://github.com/smarie/python-pytest-cases/issues/6).

### 0.3.0 - case generators

 * New decorator `@cases_generator` to define case generators. Fixes [#1](https://github.com/smarie/python-pytest-cases/issues/1).
 * Also, removed unused functions `is_expected_error_instance` and `assert_exception_equal`

### 0.2.0 - THIS_MODULE constant + Tagging/Filtering + doc

 * New constant `THIS_MODULE` so that cases and test functions can coexist in the same file. This fixes [#5](https://github.com/smarie/python-pytest-cases/issues/5).

 * Added `@test_target` and `@case_tags` decorators for case functions, and added `filter` parameter in `@cases_data`. This allows users to :
 
     * tag a case function with any item (and in particular with the reference to the function it relates to), 
     * and to filter the case functions used by a test function according to a particular tag.

   This fixes [#4](https://github.com/smarie/python-pytest-cases/issues/4).

 * Improved documentation

### 0.1.0 - First public version

 * Initial fork from private repo
