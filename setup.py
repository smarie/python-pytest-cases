"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from os import path
import pkg_resources
from setuptools import setup, find_packages

pkg_resources.require("setuptools>=39.2")
pkg_resources.require("setuptools_scm")

from setuptools_scm import get_version  # noqa: E402

# *************** Dependencies *********
INSTALL_REQUIRES = ['decopatch', 'makefun>=1.9.5',  # note: pytest, too :)
                    'functools32;python_version<"3.2"', 'funcsigs;python_version<"3.3"',
                    ]
DEPENDENCY_LINKS = []
SETUP_REQUIRES = ['pytest-runner', 'setuptools_scm']
TESTS_REQUIRE = ['pytest', 'pytest-logging', 'pytest-steps', 'pytest-harvest']
EXTRAS_REQUIRE = {}

# ************** ID card *****************
DISTNAME = 'pytest-cases'
DESCRIPTION = 'Separate test code from test cases in pytest.'
MAINTAINER = 'Sylvain MARIE'
MAINTAINER_EMAIL = 'sylvain.marie@schneider-electric.com'
URL = 'https://github.com/smarie/python-pytest-cases'
DOWNLOAD_URL = URL + '/tarball/' + get_version()
LICENSE = 'BSD 3-Clause'
LICENSE_LONG = 'License :: OSI Approved :: BSD License'
KEYWORDS = 'pytest test case testcase test-case decorator parametrize parameter data dataset file separate concerns'

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'docs', 'long_description.md')) as f:
    LONG_DESCRIPTION = f.read()

# OBSOLETES = []

setup(
    name=DISTNAME,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    # version=VERSION, NOW HANDLED BY GIT

    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,

    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',

        # Pick your license as you wish (should match "license" above)
        LICENSE_LONG,

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        'Framework :: Pytest'
    ],

    # What does your project relate to?
    keywords=KEYWORDS,

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', '*tests*']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,

    # we're using git
    use_scm_version={'write_to': '%s/_version.py' % DISTNAME.replace('-', '_')}, # this provides the version + adds the date if local non-commited changes.
    # use_scm_version={'local_scheme':'dirty-tag'}, # this provides the version + adds '+dirty' if local non-commited changes.
    setup_requires=SETUP_REQUIRES,

    # test
    # test_suite='nose.collector',
    tests_require=TESTS_REQUIRE,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require=EXTRAS_REQUIRE,

    # obsoletes=OBSOLETES

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # Note: we use the empty string so that this also works with submodules
    package_data={"": ['py.typed', '*.pyi']},
    # IMPORTANT: DO NOT set the `include_package_data` flag !! It triggers inclusion of all git-versioned files
    # see https://github.com/pypa/setuptools_scm/issues/190#issuecomment-351181286
    # include_package_data=True,

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },

    # the following makes a plugin available to pytest
    entry_points={"pytest11": ["cases = pytest_cases.plugin"]},

    # explicitly setting the flag to avoid `ply` being downloaded
    # see https://github.com/smarie/python-getversion/pull/5
    # and to make mypy happy
    # see https://mypy.readthedocs.io/en/latest/installed_packages.html
    zip_safe=False,
)
