# Changelog

### 3.8.1 - bugfixes

 - Fixed `ScopeMismatch` with parametrized cases in non-trivial test
   trees. `scope` is now correctly handled for (i) `fixture` cases, and
   (ii) fixtures defined in `conftest.py` files at any depth. Fixes
   [#311](https://github.com/smarie/python-pytest-cases/issues/311). PR
   [#317](https://github.com/smarie/python-pytest-cases/pull/317) by [@michele-riva](https://github.com/michele-riva).

### 3.8.0 - async, generators and strict-markers 

 - `@fixture` and `@parametrize` are now async and generator aware. Fixes
   [#286](https://github.com/smarie/python-pytest-cases/issues/286). PR
   [#301](https://github.com/smarie/python-pytest-cases/pull/301) by [jgersti](https://github.com/jgersti).
 - Fixed error with `pytest` `--strict-markers`. Fixes
   [#283](https://github.com/smarie/python-pytest-cases/issues/283). PR
   [#300](https://github.com/smarie/python-pytest-cases/pull/300) by [chrsmcgrr](https://github.com/chrsmcgrr).

### 3.7.0 - python 3.12

 - Added official support for Python 3.10, 3.11 and 3.12. Fixes [#314](https://github.com/smarie/python-pytest-cases/issues/314)
 - Fixed `ModuleNotFoundError: distutils` on Python 3.12 thanks to `packaging`. PR
   [#312](https://github.com/smarie/python-pytest-cases/pull/312) by [@jayqi](https://github.com/jayqi). 
 - Internal: switched to virtualenv backend.

### 3.6.14 - bugfixes

 - Fixed `AttributeError` issue in `is_case_function` when an inspected symbol is a parametrized type hint
   without `__name__`. Fixes [#287](https://github.com/smarie/python-pytest-cases/issues/287)
 - Fixed issue with `get_all_cases`: default value for `cases` was wrong. Fixes [#290](https://github.com/smarie/python-pytest-cases/issues/290)

### 3.6.13 - bugfix

 - Fixed issue where a lazy value (for example a case function) was not resolved before being injected in a parametrized function, and was therefore appearing as a `_LazyValueCaseParamValue `. Fixed [#274](https://github.com/smarie/python-pytest-cases/issues/274)

### 3.6.12 - type hint fix + enhanced compatibility with pytest plugins

 - Improved compatibility with other `pytest` plugins, in particular `pytest-repeat`, by supporting removal from fixture closure tree. Fixed [#269](https://github.com/smarie/python-pytest-cases/issues/269).
 - Fixed type hint errors detected by `pyright`. Fixed [#270](https://github.com/smarie/python-pytest-cases/issues/270)

### 3.6.11 - bugfix for pytest-xdist and `get_all_cases` API improvement

 - `get_all_cases` can now be called without `parametrization_target` (defaulting to the caller module), and with an explicit module object. Fixed [#258](https://github.com/smarie/python-pytest-cases/issues/258). PR [#260](https://github.com/smarie/python-pytest-cases/pull/260) by [@eddiebergman](https://github.com/eddiebergman).
 - Fixed `AttributeError`: module 'pytest_cases' has no attribute 'CasesCollectionWarning' when running `pytest-xdist` and at least one cases class is ignored because of `__init__` or `__new__`. Fixed [#249](https://github.com/smarie/python-pytest-cases/issues/249).

### 3.6.10 - bugfix for pytest 7.1

 - Fixed `ImportError` when using `pytest 7.1`. Fixed [#264](https://github.com/smarie/python-pytest-cases/issues/264) and [pytest-dev#9762](https://github.com/pytest-dev/pytest/issues/9762).

### 3.6.9 - Bugfix with pytest 7

 - Fixed `FrozenInstanceError` when using `pytest 7.0.0`. Fixed [#251](https://github.com/smarie/python-pytest-cases/issues/251). [PR#253](https://github.com/smarie/python-pytest-cases/pull/253) by [jammer87](https://github.com/jammer87)

### 3.6.8 - Bugfix: support for multiprocessing Pool

 - Suppressed warnings in our own tests, to improve packaging maintenance. Fixed [#248](https://github.com/smarie/python-pytest-cases/issues/248)
 - Fixed bug where setting `ids` in `@parametrize` without setting explicitly `idgen=None` would raise a `ValueError`. Fixed [#238](https://github.com/smarie/python-pytest-cases/issues/238).
 - Fixed bug where case-holding class marks were not propagated to static methods and class methods. Fixed [#246](https://github.com/smarie/python-pytest-cases/issues/246) 
 - Fixed support for multiprocessing `Pool`. Fixes [#242](https://github.com/smarie/python-pytest-cases/issues/242)

### 3.6.7 - Minor improvements and preparing for pytest 7

 - Improved error message when a case function nested in a class has no `self` argument and is not static. Fixes [#243](https://github.com/smarie/python-pytest-cases/issues/243)
 - Added support for the new Scopes enum in pytest 7. Fixed [#241](https://github.com/smarie/python-pytest-cases/issues/241)
 - Fixed `__version__` in development mode.

### 3.6.6 - Layout change

 - Restructured project so that tests are truly independent, to ease rpm/apt/etc. packaging. Fixed [#220](https://github.com/smarie/python-pytest-cases/issues/220).

### 3.6.5 - Bugfix

 - Fixed an issue where using keyword `argnames` in `@pytest.mark.parametrize` would cause `IndexError: tuple index out of range` in the tests collection phase. Fixed [#234](https://github.com/smarie/python-pytest-cases/issues/234).

### 3.6.4 - Bugfix

 - A case id can now be a reserved keyword without triggering any `SyntaxError`, even if the case is transformed into a fixture. Fixes [#230](https://github.com/smarie/python-pytest-cases/issues/230)

### 3.6.3 - Bugfix

 - Fixed an issue where a lazy value would not be resolved. This happens when the "auto-simplify fixture" happens in `@parametrize`. Fixes [#225](https://github.com/smarie/python-pytest-cases/issues/225)

### 3.6.2 - Qualimetry

 - Fixed most `flake8` errors and updated documentation to use `genbadge`. Fixes [#223](https://github.com/smarie/python-pytest-cases/issues/223)

### 3.6.1 - bugfix - parametrizing a class with `@parametrize`

 - Fixed `ValueError` when `@parametrize` is used to parametrize a class. Also, added a more explicit `TypeError` when `@parametrize` is used to parametrize a class and at least a fixture reference is present. Fixed [#215](https://github.com/smarie/python-pytest-cases/issues/215).

### 3.6.0 - `unpack_fixtures` in classes + `current_cases` improvements

 - The `current_cases` fixture now contains case parameters if any. Fixes [#214](https://github.com/smarie/python-pytest-cases/issues/214)

 - The `current_cases` fixture entries are now instances of `namedtuple`.

 - New `in_cls` argument in `unpack_fixtures` so that it can be used inside classes. Fixes [#201](https://github.com/smarie/python-pytest-cases/issues/201)

 - Fixed minor issue where empty entries could be present in `currentcases`. Fixes [#213](https://github.com/smarie/python-pytest-cases/issues/213)

### 3.5.2 - bugfix with the `currentcases` fixture

 - Fixed issues where the `currentcases` fixture would not return the correct case function. Fixed [#212](https://github.com/smarie/python-pytest-cases/issues/212)

### 3.5.1 - python 3.10 compatibility + improved error message

 - Fixed error message related to misuse of `fixture_ref`. Fixes [#209](https://github.com/smarie/python-pytest-cases/issues/209)
 - Fixed import error with python 3.10. Fixes [#207](https://github.com/smarie/python-pytest-cases/issues/207)

### 3.5.0 - New `current_cases` fixture and `get_current_cases` function + Fixes

 - New: Users can now easily access the current cases for each parametrized argument thanks to the new `current_cases` fixture. A new helper function `get_current_cases` is also provided, for direct access from a hook. `get_current_case_id` becomes deprecated in favour of these two. Fixes [#195](https://github.com/smarie/python-pytest-cases/issues/195)

 - Bugfix: Fixed issue where the cache of a `lazy_value` used for a tuple of parameters (several `argnames`) was not considering the pytest context and thus was wrongly used across pytest nodes. Fixes [#202](https://github.com/smarie/python-pytest-cases/issues/202)

 - Improved error message when a fixture parametrized with several argnames as once is not able to unpack the parameter values received (non subscriptable object).

 - `parametrize_plus` and `fixture_plus` are now deprecated in favour of `parametrize` and `fixture`, as most users seem to have adopted these names without issues.

 - (internal) Replaced the `"used"` parameter with a dedicated singleton `USED`

### 3.4.6 - Increased compatibility with other plugins 

 - `LazyValue`, `LazyTuple` and `LazyTupleItem` are now hashable. This increases compatibility with plugins hashing the parameter values, such as pytest-steps. See [pytest-steps#41](https://github.com/smarie/python-pytest-steps/issues/41) . Fixes [#199](https://github.com/smarie/python-pytest-cases/issues/199)

### 3.4.5 - Bugfix

 - Fixed bug when a test module containing `@parametrize_with_cases` was executed outside of `pytest`, typically through its `__main__`. Fixes [#198](https://github.com/smarie/python-pytest-cases/issues/198)

### 3.4.4 - Bugfix

 - Fixed issue when `@parametrize_with_cases` was used on a fixture in a `conftest.py`. Fixes [#196](https://github.com/smarie/python-pytest-cases/issues/196)

### 3.4.3 - Technical release - Zenodo

Technical release to check that Zenodo metadata is now preserved.
Same as 3.4.2, 3.4.1 and 3.4.0.

### 3.4.0 - Goodbye v1 API + Support for unbound cases + Bugfix with marks + Fixtures in case files

 - Legacy v1 API was dropped. Fixes [#192](https://github.com/smarie/python-pytest-cases/issues/192)

 - Unbound case functions in a class (e.g. `Foo.bar`) can now be directly passed to `parametrize_with_cases` without instantiating the class, e.g. `parametrize_with_cases(cases=Foo.bar)`. Fixes [#159](https://github.com/smarie/python-pytest-cases/issues/159)

 - Fixed bug with concatenation of marks on cases. Fixes [#191](https://github.com/smarie/python-pytest-cases/issues/191)

 - Fixed an issue where a case transformed into a fixture, with the same name as the fixture it requires, would lead to a `pytest` fixture recursion. 

 - Fixtures in case files can now be automatically imported using the **experimental** `@parametrize_with_cases(import_fixtures=True)`. Fixes [#193](https://github.com/smarie/python-pytest-cases/issues/193)

### 3.3.0 - Filter helpers, Current id getter, Support for `pytest-asyncio` and other plugins

 - Migrated to Github Actions + `nox` for CI/CD.

 - New helper function `get_current_case_id` to get the current case id for a given `pytest` request or item. Fixes [#189](https://github.com/smarie/python-pytest-cases/issues/189)

 - Extended the support of fixture closure modifications to `remove` and `insert(0, f)`. This in particular solves an issue with `pytest-asyncio`. Fixes [#176](https://github.com/smarie/python-pytest-cases/issues/176)

 - New `filters` module providing helper functions `has_tag`, `id_has_prefix`, `id_has_suffix`, `id_match_regex` to easily create custom filters for use in `@parametrize_with_cases(filter=...)`. PR [#184](https://github.com/smarie/python-pytest-cases/pull/184) by [@saroad2](https://github.com/saroad2), (thanks !).

### 3.2.1 - `@fixture` Bugfix

 - Fixed `fixture 'self' not found` issue when `@fixture` was used to decorate a class method not explicitly depending on `request`. Fixed [#182](https://github.com/smarie/python-pytest-cases/issues/182)

### 3.2.0 - Automatic `fixture_ref` + test ordering bugfix

 - New: from version `3.2` on, if `auto_refs=True` (default), `@parametrize` will automatically detect fixture symbols in the list of argvalues, and will create `fixture_ref`s automatically around them so that you don't need to. Fixes [#177](https://github.com/smarie/python-pytest-cases/issues/177)

 - Fixed ordering issue happening on linux targets when several `@parametrize` are used to decorate the same function. Fixes [#180](https://github.com/smarie/python-pytest-cases/issues/180)

### 3.1.2 - Bugfixes with nesting and pytest-asyncio

 - Now appending fixtures to the closure once it has been built is supported. This fixes an issue with `pytest-asyncio`. Fixes [#176](https://github.com/smarie/python-pytest-cases/issues/176)

 - Fixed issue when `parametrize_with_cases` was used on case functions themselves (nesting/recursion). This was due to a lack of support of the `place_as` magic pytest attribute. Fixes [#179](https://github.com/smarie/python-pytest-cases/issues/179)

 - Added a warning concerning usage of indirect in parametrize when fixture references are present. See [#150](https://github.com/smarie/python-pytest-cases/issues/150)

### 3.1.1 - Bugfix with ids

 - Fixed issue with Empty id marker leaking to test ids. Fixed [#171](https://github.com/smarie/python-pytest-cases/issues/171)

### 3.1.0 - Improved cases collection

 - `@parametrize_with_cases` now by default (`cases=AUTO`) looks for both file naming patterns `test_<name>_cases.py` and `cases_<name>.py`. Removed the `AUTO2` constant. Fixed [#140](https://github.com/smarie/python-pytest-cases/issues/140)

 - Nested classes containing case functions are now officially supported (they were, but undocumented). Fixed [#160](https://github.com/smarie/python-pytest-cases/issues/160)

 - Case functions that are `staticmethod` and `classmethod` are now supported as well. Fixes [#168](https://github.com/smarie/python-pytest-cases/issues/168)

### 3.0.0 - harmonization of ids and public API for cases info

 - Major refactoring of the way ids and marks are generated and customized in `fixture_union`, `@parametrize` and `@parametrize_with_cases`. Now `idstyle` has a consistent behaviour across the board, `ids` and `idstyle` can work together correctly, `@parametrize_with_cases` and `@parametrize` have much better default values for ids, and many others. See [documentation](./index.md) for details. Fixed [#154](https://github.com/smarie/python-pytest-cases/issues/154)

 - New public API to manipulate information about a case function: `copy_case_info`, `set_case_id`, `get_case_id`, `get_case_marks`, `get_case_tags`, `matches_tag_query`, `is_case_class`, `is_case_function`. See [API reference](./api_reference.md).

 - Fixed default behaviour of `idgen` in `@parametrize`: it only defaults to `AUTO` when no `fixture_ref` are used in the argvalues.

### 2.7.2 - Bugfix with doctest

 - Fixed `AttributeError: 'DoctestItem' object has no attribute '_request'` when executing doctests. Fixes [#156](https://github.com/smarie/python-pytest-cases/issues/156)

### 2.7.1 - `@pytest.mark.usefixtures` can be used on case functions 

 - `@pytest.mark.usefixtures` can be now be used on case functions. Fixes [#152](https://github.com/smarie/python-pytest-cases/issues/152).

### 2.7.0 - `@parametrize_with_cases` now supports id customization

 - `@parametrize_with_cases` now explicitly supports all id customization methods (`ids`, `idgen` and `idstyle`) supported by `@parametrize` (`ids`, `idgen` and `idstyle`). Updated documentation accordingly. Fixed [#151](https://github.com/smarie/python-pytest-cases/issues/151)

### 2.6.0 - better cache for lazy values and support for infinite id generators

 - `lazy_value` parameters are now cached by pytest node id only. So plugins can access the value without triggering an extra function call, but a new call is triggered for each pytest node, so as to prevent mutable object leakage across tests. Fixed [#149](https://github.com/smarie/python-pytest-cases/issues/149) while ensuring no regression for [#143](https://github.com/smarie/python-pytest-cases/issues/143).
 
 - The `ids` argument of `parametrize` now accepts a (possibly infinite) generator of ids, e.g. (`f"foo{i}" for i in itertools.count()`), just as `pytest` does. This was not always the case, inparticular when parametrizing a `@fixture`. The `ids` arguments of `fixture_union`, `param_fixture[s]`, etc. now also support this pattern. Fixed [#148](https://github.com/smarie/python-pytest-cases/issues/148)

### 2.5.0 - case ids `glob` match improvements

 - Improved description for the `glob` argument in `@parametrize_with_cases`. Also made the implementation escape all regex special characters so that they can't be used. Finally a pattern should now match the entire case id (previously, a partial match would work if it was at the beginning of the string). One step towards [#147](https://github.com/smarie/python-pytest-cases/issues/147)

### 2.4.0 - various fixes for test ids and lazy values

 - `is_lazy` is now part of public API, and `_LazyValue` now has a cache mechanism like `_LazyTuple`. Fixes [#143](https://github.com/smarie/python-pytest-cases/issues/143)

 - `@parametrize`: custom `ids` are now correctly taken into account when a single `lazy_value`is used for a tuple of parameters. This issue could be seen also with `@parametrize_with_cases`: `idgen` does not seem to be taken into account when cases are unpacked into a tuple. Fixes [#144](https://github.com/smarie/python-pytest-cases/issues/144).

 - Empty case ids are now replaced with `'<empty_case_id>'` to avoid ambiguous interpretation of test ids. Fixes [#142](https://github.com/smarie/python-pytest-cases/issues/142).


### 2.3.0 - better `LazyValue` internal API

 - new `clone(self, remove_int_base=False)` API on `LazyValue` and `LazyTupleItem` instances. With this new API, on old `pytest` `< 5.3`, other plugins such as `pytest-harvest` can easily clone the contents from lazy values without having them inherit from `int` - which was a dirty hack used by `pytest-cases` to trick `pytest` to generate acceptable test ids in these old pytest versions. Also improved the `LazyValue`, `LazyTuple` and `LazyTupleItem` object model with equality and repr. Fixes [pytest-harvest#43](https://github.com/smarie/python-pytest-harvest/issues/43)

### 2.2.5 - Marks are now correctly propagated from Case class

 - Marks set on a case class are now propagated to cases in the class. So you can use for example [`pytest-pilot`](https://smarie.github.io/python-pytest-pilot/) more easily ! Fixes [#139](https://github.com/smarie/python-pytest-cases/issues/139)

### 2.2.4 - Fixes issue 

 - Fixed "Created fixture names are not unique, please report" error when duplicate fixture reference is provided in a pytest.param. Fixes [#138](https://github.com/smarie/python-pytest-cases/issues/138).

### 2.2.3 - Fixed issue with pytest `3.X`

 - Fixed `TypeError: _idval() got an unexpected keyword argument 'item'` with `pytest` versions between 3.0.0 and 3.7.4. Fixed [#136](https://github.com/smarie/python-pytest-cases/issues/136)

### 2.2.2 - `@parametrize_with_cases` compatibility improvements

 - `@parametrize_with_cases` now supports that `argnames` is a list or tuple, just as `@pytest.mark.parametrize` does. PR [#132](https://github.com/smarie/python-pytest-cases/pull/132), by [`@saroad2`](https://github.com/saroad2).

### 2.2.1 - setup.py fix to enforce dependency version

 - Now enforcing usage of `makefun` 1.9.3 or above to avoid issue `AttributeError: 'functools.partial' object has no attribute '__module__'` mentioned in [#128](https://github.com/smarie/python-pytest-cases/issues/128)

### 2.2.0 - Doc improvements + bugfix for cases requiring fixtures

 - Improved documentation to explain why `@fixture` should be used instead of `@pytest.fixture`. Fixed [#125](https://github.com/smarie/python-pytest-cases/issues/125)

 - Fixed ` ValueError: fixture is being applied more than once to the same function` when two functions parametrized with the same cases were sitting in the same file. Improved robustness when cases require fixtures, in particular when parametrized test/fixture sits in a class or when several of them sit in a class/module. Fixed [#126](https://github.com/smarie/python-pytest-cases/issues/126)

### 2.1.3 - Missing deprecation warning

 - Added missing deprecation warning on `@cases_generator`. Fixes [#124](https://github.com/smarie/python-pytest-cases/issues/124).

 - Removed `target` and `tags` arguments of `@cases_generator` (deprecated api anyway) that were added by mistake in version 2.0.0 but never used.

### 2.1.2 - Compatibility fix

 - Added support for pytest items without funcargs. Fixes interoperability with other pytest plugins such as `pytest-black` or `pytest-flake8`. Fixes [#122](https://github.com/smarie/python-pytest-cases/issues/122)

### 2.1.1 - Fixed issue with pytest 6

`pytest` 6 is now supported. Fixes [#121](https://github.com/smarie/python-pytest-cases/issues/121) 

### 2.1.0 - Internal engine improvements + bugfixes

Fixed issue with `@parametrize_with_cases` when two cases with the same id and both requiring a fixture were to be created. Fixed [#117](https://github.com/smarie/python-pytest-cases/issues/117).

Fixture closure engine refactoring:

 - When no fixture unions are present, the fixture closure is now identical to the default one in `pytest`, to avoid issues originating from other plugins fiddling with the closure. Fixes [#116](https://github.com/smarie/python-pytest-cases/issues/116)

 - New `SuperClosure` class representing the "list" facade on top of the fixture tree (instead of `FixtureClosureNode`). In addition, this list facade now better handles editing the order of fixtures when possible. Fixes [#111](https://github.com/smarie/python-pytest-cases/issues/111).

 - Session and Module-scoped fixtures that are not used in all union alternatives are not any more torn town/setup across union alternatives. Fixes [#120](https://github.com/smarie/python-pytest-cases/issues/120)

### 2.0.4 - Bugfix

 - Fixed `TypeError` with iterable argvalue in standard parametrize. Fixed [#115](https://github.com/smarie/python-pytest-cases/issues/115).

### 2.0.3 - Bugfixes

 - Fixed wrong module string decomposition when passed to `cases` argument in `@parametrize_with_cases`. Fixes [#113](https://github.com/smarie/python-pytest-cases/issues/113)

 - Autouse fixtures are now correctly used. Fixed [#114](https://github.com/smarie/python-pytest-cases/issues/114)

### 2.0.2 - Better string representation for lazy values

Lazy values (so, test cases) now have a much nicer string representation ; in particular in `pytest-harvest` results tables. Fixes [#112](https://github.com/smarie/python-pytest-cases/issues/112)

### 2.0.1 - Better test ids and theory page

 - New documentation page concerning theory of fixture unions. Fixes [#109](https://github.com/smarie/python-pytest-cases/issues/109)

 - Using a `fixture_ref` in a new-style `@parametrize` (with `**args` or `idgen`) now outputs a correct id. Fixes [#110](https://github.com/smarie/python-pytest-cases/issues/110)

### 2.0.0 - Less boilerplate & full `pytest` alignment

I am very pleased to announce this new version of `pytest-cases`, providing a lot of **major** improvements. Creating powerful and complex test suites have never been so easy and intuitive !

Below is a complete list of changes, but the user guide has also been updated accordingly so feel free to [have a look](index.md) to get a complete example-based walkthrough.


**A/ More powerful and flexible cases collection**

New [`@parametrize_with_cases`](./api_reference.md#parametrize_with_cases) decorator to replace `@cases_data` (deprecated).

 1. Aligned with `pytest`: 
 
    - now `argnames` can contain several names, and the case functions are **automatically unpacked** into it. You don't need to perform a `case.get()` in the test anymore !

            @parametrize_with_cases("a,b")
            def test_foo(a, b):
                # use a and b directly !
                ...

    - cases are unpacked at test *setup* time, so *the clock does not run while the case is created* - in case you use `pytest-harvest` to collect the timings.

    - `@parametrize_with_cases` can be used on test functions *as well as fixture functions* (it was already the case in v1)


 2. Easier to configure: 
 
     - the decorator now has a single `cases` argument to indicate the cases, wherever they come from (no `module` argument anymore)

     - default (`cases=AUTO`) *automatically looks for cases in the associated case module* named `test_xxx_cases.py`. Users can easily switch to alternate pattern `cases_xxx.py` with `cases=AUTO2`. Fixes [#91](https://github.com/smarie/python-pytest-cases/issues/91).
    
     - **cases can sit inside a class**, like [what you're used to do with `pytest`](https://docs.pytest.org/en/stable/getting-started.html#group-multiple-tests-in-a-class). This additional style makes it much more convenient to organize cases and associated them with tests, when cases sit in the same file than the tests. Fixes [#93](https://github.com/smarie/python-pytest-cases/issues/93).
     
     - an explicit sequence can be provided, *it can mix all kind of sources*: functions, classes, modules, and *module names as strings* (even relative ones!).

            @parametrize_with_cases("a", cases=(CasesClass, '.my_extra_cases'))
            def test_foo(a):
                ...


 3. More powerful API for filtering:
 
     - a new `prefix` argument (default `case_`) can be used to define case functions for various type of parameters: welcome `user_<id>`, `data_<id>`, `algo_<id>`, `model_<id>` ! Fixes [#108](https://github.com/smarie/python-pytest-cases/issues/108)
     
     - a new `glob` argument receiving a glob-like string can be used to further filter cases based on their names. For example you can distinguish `*_success` from `*_failure` case ids, so as to dispatch them to the appropriate positive or negative test. Fixes [#108](https://github.com/smarie/python-pytest-cases/issues/108)
     
     - finally you can still use `has_tag` and/or provide a `filter` callable, but now the callable will receive the case function, and this case function has a `f._pytestcase` attribute containing the id, tags and marks - it is therefore much easier to implement custom filtering.


**B/ Easier-to-define case functions**

 - Case functions can start with different prefixes to denote different kind of data: e.g. `data_<id>`, `user_<id>`, `model_<id>`, etc.

 - Case functions can now be parametrized with [`@parametrize`](pytest_goodies.md#parametrize) or `@pytest.mark.parametrize`, just as in pytest ! This includes the ability to put [`pytest` marks](https://docs.pytest.org/en/stable/mark.html) on the whole case, or on some specific parameter values using [`pytest.param`](https://docs.pytest.org/en/stable/example/parametrize.html#set-marks-or-test-id-for-individual-parametrized-test). `@cases_generator` is therefore now deprecated but its alternate style for ids and arguments definition was preserved in `@parametrize`, see below. 

 - Now case functions can require fixtures ! In that case they will be transformed into fixtures and injected as `fixture_ref` in the parametrization. Fixes [#56](https://github.com/smarie/python-pytest-cases/issues/56).

 - New single optional `@case(id=None, tags=(), marks=())` decorator to replace `@case_name` and `@case_tags` (deprecated): a single simple way to customize all aspects of a case function. Also, `@test_target` completely disappears from the picture as it was just a tag like others - this could be misleading.


**C/ Misc / pytest goodies**

 - New aliases for readability: `@fixture` for `@fixture_plus`, and`@parametrize` for `@parametrize_plus` (both aliases will coexist with the old names). Fixes [#107](https://github.com/smarie/python-pytest-cases/issues/107).

 - `@parametrize` was improved in order to support the alternate parametrization mode that was previously offered by `@cases_generator`, see [api reference](api_reference.md#parametrize). That way, users will be able to choose the style of their choice. Fixes [#57](https://github.com/smarie/python-pytest-cases/issues/57) and [#106](https://github.com/smarie/python-pytest-cases/issues/106).

 - `@parametrize` now raises an explicit error message when the user makes a mistake with the argnames. Fixes [#105](https://github.com/smarie/python-pytest-cases/issues/105).

 - More readable error messages in `@parametrize` when `lazy_value` does not return the same number of argvalues than expected from the argnames.

 - Any error message associated to a `lazy_value` function call is not caught and hidden anymore but is emitted to the user, for easier debugging.
 
 - Fixed issue with `lazy_value` when a single mark is passed in the constructor.

 - `lazy_value` used as a tuple for several arguments now have a correct id generated even in old pytest version 2.
 
 - New pytest goodie `assert_exception` that can be used as a context manager. Fixes [#104](https://github.com/smarie/python-pytest-cases/issues/104).


### 1.17.0 - `lazy_value` improvements + annoying warnings suppression

 - `lazy_value` are now resolved at pytest `setup` stage, not pytest `call` stage. This is important for execution time recorded in the reports (see also `pytest-harvest` plugin). Fixes [#102](https://github.com/smarie/python-pytest-cases/issues/102) 

 - A function used as a `lazy_value` can now be marked with pytest marks. Fixes [#99](https://github.com/smarie/python-pytest-cases/issues/99)

 - A `lazy_value` now has a nicer id when it is a partial. Fixes [#97](https://github.com/smarie/python-pytest-cases/issues/97)
 
 - Removed annoying `PytestUnknownMarkWarning` warning message when a mark was used on a case. Fixes [#100](https://github.com/smarie/python-pytest-cases/issues/100)

### 1.16.0 - New `lazy_value` for parameters

 - New marker `lazy_value` for `parametrize_plus`. Fixes [#92](https://github.com/smarie/python-pytest-cases/issues/92)

### 1.15.0 - better `parametrize_plus` and smaller dependencies

 - Better support for `pytest.param` in `parametrize_plus` and also in `fixture_union` and `fixture_param[s]`. Improved corresponding ids. Fixed [#79](https://github.com/smarie/python-pytest-cases/issues/79) and [#86](https://github.com/smarie/python-pytest-cases/issues/86)
 
 - New `@ignore_unused` decorator to protect a fixture function from the "NOT_USED" case happening when the fixture is used in a fixture union.
  
 - Removed `six`, `wrapt` and `enum34` dependencies

 - (Internal) submodules reorganization for readability
 - (Internal) suppressed a lot of code quality warnings

### 1.14.0 - bugfixes and hook feature

 - Fixed `ids` precedence order when using `pytest.mark.parametrize` in a `fixture_plus`. Fixed [#87](https://github.com/smarie/python-pytest-cases/issues/87)

 - Fixed issue with `fixture_union` when using the same fixture twice in it. Fixes [#85](https://github.com/smarie/python-pytest-cases/issues/85)

 - Added the possibility to pass a `hook` function in all API where fixtures are created behind the scenes, so as to ease debugging and/or save fixtures (with `stored_fixture` from pytest harvest). Fixes [#83](https://github.com/smarie/python-pytest-cases/issues/83)
 
 - Fixture closures now support reordering when no unions are present. This suppressed the annoying warning "WARNING the new order is not taken into account !!" when it was not relevant. Fixes [#81](https://github.com/smarie/python-pytest-cases/issues/81)

### 1.13.1 - packaging improvements

 - packaging improvements: set the "universal wheel" flag to 1, and cleaned up the `setup.py`. In particular removed dependency to `six` for setup and added `py.typed` file. Fixes [#78](https://github.com/smarie/python-pytest-cases/issues/78)

### 1.13.0 - `@cases_generator` default `names`

`@cases_generator` now has a default value for the `names` template, based on the parameters. Fixes [#77](https://github.com/smarie/python-pytest-cases/issues/77).

### 1.12.4 - Bugfix

Fixed `ValueError` when a product of unions was used on a test node, for example when two `parametrize_plus` using `fixture_ref`s were used on the same fixture or test function. Fixed [#76](https://github.com/smarie/python-pytest-cases/issues/76)

### 1.12.3 - Improved error messages

Improved error message when something that is not a fixture is used in `unpack_fixture` or `fixture_union`. Fixed [#75](https://github.com/smarie/python-pytest-cases/issues/75)

### 1.12.2 - Warning fix

Fixed deprecation warning [#74](https://github.com/smarie/python-pytest-cases/issues/74)

### 1.12.1 - Bugfixes

 - Now using module name and not file path to detect symbols in cases files that are imported from elsewhere and not created locally. Indeed that was causing problems on some ^platforms where a `.pyc` cache file is created. Fixes [#72](https://github.com/smarie/python-pytest-cases/issues/72)

 - Fixed `PluginValidationError` when `pytest_fixture_plus` or `pytest_parametrize_plus` were used in a `conftest.py` file. Fixes [#71](https://github.com/smarie/python-pytest-cases/issues/71). According to discussion in [pytest#6475](https://github.com/pytest-dev/pytest/issues/6475), `pytest_fixture_plus` and `pytest_parametrize_plus` are now renamed to `fixture_plus` and `parametrize_plus` in order for pytest (pluggy) not to think they are hooks. Old aliases will stay around for a few versions, with a deprecation warning.

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

New commandline option '--with-reorder' to change the reordering strategy currently in application. Fixes [#45](https://github.com/smarie/python-pytest-cases/issues/45).

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

`@pytest_fixture_plus` now correctly honors parameter id and marks overridden at single parameter level using `pytest.param`. Fixed [#30](https://github.com/smarie/python-pytest-cases/issues/30).

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
