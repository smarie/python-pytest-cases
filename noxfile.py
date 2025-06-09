import logging

import nox  # noqa
from pathlib import Path  # noqa
import sys

# add parent folder to python path so that we can import noxfile_utils.py
# note that you need to "pip install -r noxfile-requiterements.txt" for this file to work.
sys.path.append(str(Path(__file__).parent / "ci_tools"))
from nox_utils import (PY39, PY310, PY311, PY312, PY313, PY314, install_reqs, rm_folder, rm_file, DONT_INSTALL)  # noqa


pkg_name = "pytest_cases"
gh_org = "smarie"
gh_repo = "python-pytest-cases"


# set the default activated sessions, minimal for CI
nox.options.sessions = ["tests", "flake8", "docs", "build"]  # , "docs", "gh_pages"
nox.options.error_on_missing_interpreters = True
nox.options.reuse_existing_virtualenvs = True  # this can be done using -r
# if platform.system() == "Windows":  >> always use this for better control
nox.options.default_venv_backend = "virtualenv"
# os.environ["NO_COLOR"] = "True"  # nox.options.nocolor = True does not work
# nox.options.verbose = True

nox_logger = logging.getLogger("nox")
# nox_logger.setLevel(logging.INFO)  NO !!!! this prevents the "verbose" nox flag to work !


class Folders:
    root = Path(__file__).parent
    ci_tools = root / "ci_tools"
    runlogs = root / Path(nox.options.envdir or ".nox") / "_runlogs"
    runlogs.mkdir(parents=True, exist_ok=True)
    dist = root / "dist"
    site = root / "site"
    site_reports = site / "reports"
    reports_root = root / "docs" / "reports"
    test_reports = reports_root / "junit"
    test_xml = test_reports / "junit.xml"
    test_html = test_reports / "report.html"
    test_badge = test_reports / "junit-badge.svg"
    coverage_reports = reports_root / "coverage"
    coverage_xml = coverage_reports / "coverage.xml"
    coverage_intermediate_file = root / ".coverage"
    coverage_badge = coverage_reports / "coverage-badge.svg"
    flake8_reports = reports_root / "flake8"
    flake8_intermediate_file = root / "flake8stats.txt"
    flake8_badge = flake8_reports / "flake8-badge.svg"


ENVS = {
    # python 3.14
    (PY314, "pytest-latest"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": ""}},
    (PY314, "pytest7.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<8"}},
    (PY314, "pytest6.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<7"}},
    # python 3.13
    (PY313, "pytest-latest"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": ""}},
    (PY313, "pytest7.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<8"}},
    (PY313, "pytest6.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<7"}},
    # python 3.12
    (PY312, "pytest-latest"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": ""}},
    (PY312, "pytest7.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<8"}},
    (PY312, "pytest6.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<7"}},
    # python 3.11
    # We'll run 'pytest-latest' this last for coverage
    (PY311, "pytest7.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<8"}},
    (PY311, "pytest6.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<7"}},
    # python 3.10
    (PY310, "pytest-latest"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": ""}},
    (PY310, "pytest7.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<8"}},
    (PY310, "pytest6.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<7"}},
    # python 3.9
    (PY39, "pytest-latest"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": ""}},
    (PY39, "pytest7.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<8"}},
    (PY39, "pytest6.x"): {"coverage": False, "pkg_specs": {"pip": ">19", "pytest": "<7"}},
    # IMPORTANT: this should be last so that the folder docs/reports is not deleted afterwards
    (PY311, "pytest-latest"): {"coverage": True, "pkg_specs": {"pip": ">19", "pytest": ""}},
}

ENV_PARAMS = tuple((k[0], v["coverage"], v["pkg_specs"]) for k, v in ENVS.items())
ENV_IDS = tuple(f"{k[0].replace('.', '-')}-env-{k[1]}" for k in ENVS)


@nox.session
@nox.parametrize("python,coverage,pkg_specs", ENV_PARAMS, ids=ENV_IDS)
def tests(session, coverage, pkg_specs):
    """Run the test suite, including test reports generation and coverage reports. """

    # As soon as this runs, we delete the target site and coverage files to avoid reporting wrong coverage/etc.
    rm_folder(Folders.site)
    rm_folder(Folders.reports_root)
    # delete the .coverage files if any (they are not supposed to be any, but just in case)
    rm_file(Folders.coverage_intermediate_file)
    rm_file(Folders.root / "coverage.xml")

    # CI-only dependencies
    # Did we receive a flag through positional arguments ? (nox -s tests -- <flag>)
    # install_ci_deps = False
    # if len(session.posargs) == 1:
    #     assert session.posargs[0] == "keyrings.alt"
    #     install_ci_deps = True
    # elif len(session.posargs) > 1:
    #     raise ValueError("Only a single positional argument is accepted, received: %r" % session.posargs)

    # uncomment and edit if you wish to uninstall something without deleting the whole env
    # session.run2("pip uninstall pytest-asyncio --yes")

    # install all requirements
    install_reqs(session, setup=True, install=True, tests=True, versions_dct=pkg_specs)

    # install CI-only dependencies
    # if install_ci_deps:
    #     session.install2("keyrings.alt")

    # list all (conda list alone does not work correctly on github actions)
    # session.run2("conda list")
    # conda_prefix = Path(session.bin)
    # if conda_prefix.name == "bin":
    #     conda_prefix = conda_prefix.parent
    # session.run2("conda list", env={"CONDA_PREFIX": str(conda_prefix), "CONDA_DEFAULT_ENV": session.get_session_id()})

    # Fail if the assumed python version is not the actual one
    session.run("python", "ci_tools/check_python_version.py", session.python)

    # check that it can be imported even from a different folder
    # Important: do not surround the command into double quotes as in the shell !
    # session.run('python', '-c', 'import os; os.chdir(\'./docs/\'); import %s' % pkg_name)

    # finally run all tests
    if not coverage:
        # install self so that it is recognized by pytest
        session.install(".", "--no-deps")

        # simple: pytest only
        session.run("python", "-m", "pytest", "--cache-clear", "-v", "tests/")
    else:
        # install self in "develop" mode so that coverage can be measured
        session.install("-e", ".", "--no-deps")

        # coverage + junit html reports + badge generation
        install_reqs(session, phase="coverage",
                             phase_reqs=["coverage", "pytest-html", "genbadge[tests,coverage]"],
                             versions_dct=pkg_specs)

        # --coverage + junit html reports
        session.run("coverage", "run", "--source", f"src/{pkg_name}",
                    "-m", "pytest", "--cache-clear",
                    f"--junitxml={Folders.test_xml}", f"--html={Folders.test_html}",
                    "-v", "tests/")
        session.run("coverage", "report")  # this shows in terminal + fails under XX%, same as --cov-report term --cov-fail-under=70  # noqa
        session.run("coverage", "xml", "-o", f"{Folders.coverage_xml}")
        session.run("coverage", "html", "-d", f"{Folders.coverage_reports}")
        # delete this intermediate file, it is not needed anymore
        rm_file(Folders.coverage_intermediate_file)

        # --generates the badge for the test results and fail build if less than x% tests pass
        nox_logger.info("Generating badge for tests coverage")
        # Use our own package to generate the badge
        session.run("genbadge", "tests", "-i", f"{Folders.test_xml}", "-o", f"{Folders.test_badge}", "-t", "100")
        session.run("genbadge", "coverage", "-i", f"{Folders.coverage_xml}", "-o", f"{Folders.coverage_badge}")


@nox.session(python=PY311)
def flake8(session):
    """Launch flake8 qualimetry."""

    session.install("-r", str(Folders.ci_tools / "flake8-requirements.txt"))
    session.install(".")

    rm_folder(Folders.flake8_reports)
    Folders.flake8_reports.mkdir(parents=True, exist_ok=True)
    rm_file(Folders.flake8_intermediate_file)

    session.cd("src")

    # Options are set in `setup.cfg` file
    session.run("flake8", pkg_name, "--exit-zero", "--format=html", "--htmldir", str(Folders.flake8_reports),
                "--statistics", "--tee", "--output-file", str(Folders.flake8_intermediate_file))
    # generate our badge
    session.run("genbadge", "flake8", "-i", f"{Folders.flake8_intermediate_file}", "-o", f"{Folders.flake8_badge}")
    rm_file(Folders.flake8_intermediate_file)


@nox.session(python=PY311)
def docs(session):
    """Generates the doc. Pass '-- serve' to serve it on a local http server instead."""

    install_reqs(session, phase="docs", phase_reqs=["mkdocs-material", "mkdocs", "pymdown-extensions", "pygments"])

    if session.posargs:
        # use posargs instead of "build"
        session.run("mkdocs", *session.posargs)
    else:
        session.run("mkdocs", "build")


@nox.session(python=PY311)
def publish(session):
    """Deploy the docs+reports on github pages. Note: this rebuilds the docs"""

    install_reqs(session, phase="publish", phase_reqs=["mkdocs-material", "mkdocs", "pymdown-extensions", "pygments"])

    # possibly rebuild the docs in a static way (mkdocs serve does not build locally)
    session.run("mkdocs", "build")

    # check that the doc has been generated with coverage
    if not Folders.site_reports.exists():
        raise ValueError("Test reports have not been built yet. Please run 'nox -s tests(3.7)' first")

    # publish the docs
    session.run("mkdocs", "gh-deploy")

    # publish the coverage - now in github actions only
    # install_reqs(session, phase="codecov", phase_reqs=["codecov", "keyring"])
    # # keyring set https://app.codecov.io/gh/<org>/<repo> token
    # import keyring  # (note that this import is not from the session env but the main nox env)
    # codecov_token = keyring.get_password("https://app.codecov.io/gh/<org>/<repo>>", "token")
    # # note: do not use --root nor -f ! otherwise "There was an error processing coverage reports"
    # session.run2('codecov -t %s -f %s' % (codecov_token, Folders.coverage_xml))


def _build(session):
    """Common code used by build and release sessions"""
    install_reqs(session, setup=True, phase="setup.py#dist", phase_reqs=["setuptools_scm"])

    # Get current tag using setuptools_scm and make sure this is not a dirty/dev one
    from setuptools_scm import get_version  # (note that this import is not from the session env but the main nox env)
    from setuptools_scm.version import guess_next_dev_version
    version = []

    def my_scheme(version_):
        version.append(version_)
        return guess_next_dev_version(version_)

    current_tag = get_version(".", version_scheme=my_scheme)

    # create the package
    rm_folder(Folders.dist)

    session.run("python", "setup.py", "sdist", "bdist_wheel")

    # Make sure that the generated _version.py file exists
    version_py = Path(f"src/{pkg_name}/_version.py")
    if not version_py.exists():
        raise ValueError("Error with setuptools_scm: _version.py file not generated")

    # ...and is compliant with python 2.7
    # if ":" in version_py.read_text():
    #     raise ValueError("Error with setuptools_scm: _version.py file contains annotations")

    return current_tag, version


@nox.session(python=PY311)
def build(session):
    """Same as release but just builds"""

    current_tag, version = _build(session)
    print(f"current tag: {current_tag}")
    print(f"version: {version}")


@nox.session(python=PY311)
def release(session):
    """Create a release on github corresponding to the latest tag"""

    current_tag, version = _build(session)

    if version[0].dirty or not version[0].exact:
        raise ValueError("You need to execute this action on a clean tag version with no local changes.")

    # Did we receive a token through positional arguments ? (nox -s release -- <token>)
    if len(session.posargs) == 1:
        # Run from within github actions - no need to publish on pypi
        gh_token = session.posargs[0]
        publish_on_pypi = False

    elif len(session.posargs) == 0:
        # Run from local commandline - assume we want to manually publish on PyPi
        publish_on_pypi = True

        # keyring set https://docs.github.com/en/rest token
        import keyring  # (note that this import is not from the session env but the main nox env)
        gh_token = keyring.get_password("https://docs.github.com/en/rest", "token")
        assert len(gh_token) > 0

    else:
        raise ValueError("Only a single positional arg is allowed for now")

    # publish the package on PyPi
    if publish_on_pypi:
        # keyring set https://upload.pypi.org/legacy/ your-username
        # keyring set https://test.pypi.org/legacy/ your-username
        install_reqs(session, phase="PyPi", phase_reqs=["twine"])
        session.run("twine", "upload", "dist/*", "-u", "smarie")  # -r testpypi

    # create the github release
    install_reqs(session, phase="release", phase_reqs=["click", "PyGithub"])
    session.run("python", "ci_tools/github_release.py", "-s", gh_token,
                "--repo-slug", f"{gh_org}/{gh_repo}", "-cf", "./docs/changelog.md",
                "-d", f"https://{gh_org}.github.io/{gh_repo}/changelog", current_tag)


# @nox.session(python=False)
# def gha_list(session):
#     """(mandatory arg: <base_session_name>) Prints all sessions available for <base_session_name>, for GithubActions."""
#
#     # see https://stackoverflow.com/q/66747359/7262247
#
#     # The options
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-s", "--session", help="The nox base session name")
#     parser.add_argument(
#         "-v",
#         "--with_version",
#         action="store_true",
#         default=False,
#         help="Return a list of lists where the first element is the python version and the second the nox session.",
#     )
#     additional_args = parser.parse_args(session.posargs)
#
#     # Now use --json CLI option
#     out = session.run("nox", "-l", "--json", "-s", "tests", external=True, silent=True)
#     sessions_list = [{"python": s["python"], "session": s["session"]} for s in json.loads(out)]
#
#     # TODO filter ?
#
#     # print the list so that it can be caught by GHA.
#     # Note that json.dumps is optional since this is a list of string.
#     # However it is to remind us that GHA expects a well-formatted json list of strings.
#     print(json.dumps(sessions_list))


# if __name__ == '__main__':
#     # allow this file to be executable for easy debugging in any IDE
#     nox.run(globals())
