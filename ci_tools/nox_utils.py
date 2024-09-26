from collections import namedtuple
import logging
from pathlib import Path
import shutil
import os

from typing import Sequence, Dict, Union

import nox


nox_logger = logging.getLogger("nox")


PY27, PY35, PY36, PY37, PY38, PY39, PY310, PY311, PY312, PY313 = ("2.7", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10",
                                                                "3.11", "3.12", "3.13")
DONT_INSTALL = "dont_install"


def install_reqs(
    session,
    # pre wired phases
    setup=False,
    install=False,
    tests=False,
    extras=(),
    # custom phase
    phase=None,
    phase_reqs=None,
    versions_dct=None
):
    """
    A high-level helper to install requirements from the various project files

     - pyproject.toml "[build-system] requires" (if setup=True)
     - setup.cfg "[options] setup_requires" (if setup=True)
     - setup.cfg "[options] install_requires" (if install=True)
     - setup.cfg "[options] test_requires" (if tests=True)
     - setup.cfg "[options.extras_require] <...>" (if extras=(a tuple of extras))

    Two additional mechanisms are provided in order to customize how packages are installed.

    Conda packages
    --------------
    If the session runs on a conda environment, you can add a [tool.conda] section to your pyproject.toml. This
    section should contain a `conda_packages` entry containing the list of package names that should be installed
    using conda instead of pip.

    ```
    [tool.conda]
    # Declare that the following packages should be installed with conda instead of pip
    # Note: this includes packages declared everywhere, here and in setup.cfg
    conda_packages = [
        "setuptools",
        "wheel",
        "pip"
    ]
    ```

    Version constraints
    -------------------
    In addition to the version constraints in the pyproject.toml and setup.cfg, you can specify additional temporary
    constraints with the `versions_dct` argument , for example if you know that this executes on a specific python
    version that requires special care.
    For this, simply pass a dictionary of {'pkg_name': 'pkg_constraint'} for example {"pip": ">10"}.

    """

    # Read requirements from pyproject.toml
    toml_setup_reqs, toml_use_conda_for = read_pyproject_toml()
    if setup:
        install_any(session, "pyproject.toml#build-system", toml_setup_reqs,
                    use_conda_for=toml_use_conda_for, versions_dct=versions_dct)

    # Read test requirements from setup.cfg
    setup_cfg = read_setuptools_cfg()
    if setup:
        install_any(session, "setup.cfg#setup_requires", setup_cfg.setup_requires,
                    use_conda_for=toml_use_conda_for, versions_dct=versions_dct)
    if install:
        install_any(session, "setup.cfg#install_requires", setup_cfg.install_requires,
                    use_conda_for=toml_use_conda_for, versions_dct=versions_dct)
    if tests:
        install_any(session, "setup.cfg#tests_requires", setup_cfg.tests_requires,
                    use_conda_for=toml_use_conda_for, versions_dct=versions_dct)

    for extra in extras:
        install_any(session, "setup.cfg#extras_require#%s" % extra, setup_cfg.extras_require[extra],
                    use_conda_for=toml_use_conda_for, versions_dct=versions_dct)

    if phase is not None:
        install_any(session, phase, phase_reqs, use_conda_for=toml_use_conda_for, versions_dct=versions_dct)


def install_any(session,
                phase_name: str,
                pkgs: Sequence[str],
                use_conda_for: Sequence[str] = (),
                versions_dct: Dict[str, str] = None,
                ):
    """Install the `pkgs` provided with `session.install(*pkgs)`, except for those present in `use_conda_for`"""

    # use the provided versions dictionary to update the versions
    if versions_dct is None:
        versions_dct = dict()
    pkgs = [pkg + versions_dct.get(pkg, "") for pkg in pkgs if versions_dct.get(pkg, "") != DONT_INSTALL]

    nox_logger.debug("\nAbout to install *%s* requirements: %s.\n "
                     "Conda pkgs are %s" % (phase_name, pkgs, use_conda_for))

    # install on conda... if the session uses conda backend
    if not isinstance(session.virtualenv, nox.virtualenv.CondaEnv):
        conda_pkgs = []
    else:
        conda_pkgs = [pkg_req for pkg_req in pkgs if any(get_req_pkg_name(pkg_req) == c for c in use_conda_for)]
        if len(conda_pkgs) > 0:
            nox_logger.info("[%s] Installing requirements with conda: %s" % (phase_name, conda_pkgs))
            session.conda_install(*conda_pkgs)

    pip_pkgs = [pkg_req for pkg_req in pkgs if pkg_req not in conda_pkgs]
    # safety: make sure that nothing went modified or forgotten
    assert set(conda_pkgs).union(set(pip_pkgs)) == set(pkgs)
    if len(pip_pkgs) > 0:
        nox_logger.info("[%s] Installing requirements with pip: %s" % (phase_name, pip_pkgs))
        session.install(*pip_pkgs)


# ------------- requirements related


def read_pyproject_toml() -> Union[list, list]:
    """
    Reads the `pyproject.toml` and returns

     - a list of setup requirements from [build-system] requires
     - sub-list of these requirements that should be installed with conda, from [tool.my_conda] conda_packages
    """
    if os.path.exists("pyproject.toml"):
        import toml
        nox_logger.debug("\nA `pyproject.toml` file exists. Loading it.")
        pyproject = toml.load("pyproject.toml")
        requires = pyproject['build-system']['requires']
        try:
            conda_pkgs = pyproject['tool']['conda']['conda_packages']
        except KeyError:
            conda_pkgs = []
        return requires, conda_pkgs
    else:
        raise FileNotFoundError("No `pyproject.toml` file exists. No dependency will be installed ...")


SetupCfg = namedtuple('SetupCfg', ('setup_requires', 'install_requires', 'tests_requires', 'extras_require'))


def read_setuptools_cfg():
    """
    Reads the `setup.cfg` file and extracts the various requirements lists
    """
    # see https://stackoverflow.com/a/30679041/7262247
    from setuptools import Distribution
    dist = Distribution()
    dist.parse_config_files()
    return SetupCfg(setup_requires=dist.setup_requires,
                    install_requires=dist.install_requires,
                    tests_requires=dist.tests_require,
                    extras_require=dist.extras_require)


def get_req_pkg_name(r):
    """Return the package name part of a python package requirement.

    For example
    "funcsigs;python<'3.5'" will return "funcsigs"
    "pytest>=3" will return "pytest"
    """
    return r.replace('<', '=').replace('>', '=').replace(';', '=').split("=")[0]


# ----------- other goodies


def rm_file(folder: Union[str, Path]):
    """Since on windows Path.unlink throws permission error sometimes, os.remove is preferred."""
    if isinstance(folder, str):
        folder = Path(folder)

    if folder.exists():
        os.remove(str(folder))
        # Folders.site.unlink()  --> possible PermissionError


def rm_folder(folder: Union[str, Path]):
    """Since on windows Path.unlink throws permission error sometimes, shutil is preferred."""
    if isinstance(folder, str):
        folder = Path(folder)

    if folder.exists():
        shutil.rmtree(str(folder))
        # Folders.site.unlink()  --> possible PermissionError
