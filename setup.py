"""
To understand this project's build structure

 - This project uses setuptools, so it is declared as the build system in the pyproject.toml file
 - We use as much as possible `setup.cfg` to store the information so that it can be read by other tools such as `tox`
   and `nox`. So `setup.py` contains **almost nothing** (see below)
   This philosophy was found after trying all other possible combinations in other projects :)
   A reference project that was inspiring to make this move : https://github.com/Kinto/kinto/blob/master/setup.cfg

See also:
  https://setuptools.readthedocs.io/en/latest/setuptools.html#configuring-setup-using-setup-cfg-files
  https://packaging.python.org/en/latest/distributing.html
  https://github.com/pypa/sampleproject
"""
from setuptools import setup


# (1) check required versions (from https://medium.com/@daveshawley/safely-using-setup-cfg-for-metadata-1babbe54c108)
import pkg_resources

pkg_resources.require("setuptools>=39.2")
pkg_resources.require("setuptools_scm")


# (2) Generate download url using git version
from setuptools_scm import get_version  # noqa: E402

URL = "https://github.com/smarie/python-pytest-cases"
DOWNLOAD_URL = URL + "/tarball/" + get_version()


# (3) Call setup() with as little args as possible
setup(
    download_url=DOWNLOAD_URL,
    use_scm_version={
        "write_to": "src/pytest_cases/_version.py"
    },  # we can't put `use_scm_version` in setup.cfg yet unfortunately
)
