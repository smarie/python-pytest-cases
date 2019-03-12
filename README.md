# pytest-cases

Separate test code from test cases in `pytest`.

[![Python versions](https://img.shields.io/pypi/pyversions/pytest-cases.svg)](https://pypi.python.org/pypi/pytest-cases/) [![Build Status](https://travis-ci.org/smarie/python-pytest-cases.svg?branch=master)](https://travis-ci.org/smarie/python-pytest-cases) [![Tests Status](https://smarie.github.io/python-pytest-cases/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-pytest-cases/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-pytest-cases/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-pytest-cases)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-pytest-cases/) [![PyPI](https://img.shields.io/pypi/v/pytest-cases.svg)](https://pypi.python.org/pypi/pytest-cases/) [![Downloads](https://pepy.tech/badge/pytest-cases)](https://pepy.tech/project/pytest-cases) [![Downloads per week](https://pepy.tech/badge/pytest-cases/week)](https://pepy.tech/project/pytest-cases) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-pytest-cases.svg)](https://github.com/smarie/python-pytest-cases/stargazers)

**This is the readme for developers.** The documentation for users is available here: [https://smarie.github.io/python-pytest-cases/](https://smarie.github.io/python-pytest-cases/)

## Want to contribute ?

Contributions are welcome ! Simply fork this project on github, commit your contributions, and create pull requests.

Here is a non-exhaustive list of interesting open topics: [https://github.com/smarie/python-pytest-cases/issues](https://github.com/smarie/python-pytest-cases/issues)

## Running the tests

This project uses `pytest`.

```bash
pytest -v pytest_cases/tests/
```

You may need to install requirements for setup beforehand, using 

```bash
pip install -r ci_tools/requirements-test.txt
```

## Packaging

This project uses `setuptools_scm` to synchronise the version number. Therefore the following command should be used for development snapshots as well as official releases: 

```bash
python setup.py egg_info bdist_wheel rotate -m.whl -k3
```

You may need to install requirements for setup beforehand, using 

```bash
pip install -r ci_tools/requirements-setup.txt
```

## Generating the documentation page

This project uses `mkdocs` to generate its documentation page. Therefore building a local copy of the doc page may be done using:

```bash
mkdocs build -f docs/mkdocs.yml
```

You may need to install requirements for doc beforehand, using 

```bash
pip install -r ci_tools/requirements-doc.txt
```

## Generating the test reports

The following commands generate the html test report and the associated badge. 

```bash
pytest --junitxml=junit.xml -v pytest_cases/tests/
ant -f ci_tools/generate-junit-html.xml
python ci_tools/generate-junit-badge.py
```

### PyPI Releasing memo

This project is now automatically deployed to PyPI when a tag is created. Anyway, for manual deployment we can use:

```bash
twine upload dist/* -r pypitest
twine upload dist/*
```
