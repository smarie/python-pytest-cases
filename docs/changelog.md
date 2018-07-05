# Changelog

### 0.2.0 - THIS_MODULE constant + Tagging/Filtering + doc

 * New constant `THIS_MODULE` so that cases and test functions can coexist in the same file. This fixes [#5](https://github.com/smarie/python-pytest-cases/issues/5)

 * Added `@test_target` and `@case_tags` decorators for case functions, and added `filter` parameter in `@cases_data`. This allows users to :
 
     * tag a case function with any item (and in particular with the reference to the function it relates to), 
     * and to filter the case functions used by a test function according to a particular tag.

   This fixes [#4](https://github.com/smarie/python-pytest-cases/issues/4)

 * Improved documentation

### 0.1.0 - First public version

 * Initial fork from private repo
