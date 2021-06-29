from itertools import product

import asyncio
from collections import namedtuple
from inspect import signature, isfunction
import logging
from pathlib import Path
import shutil
import subprocess
import sys
import os

from typing import Sequence, Dict, Union, Iterable, Mapping, Any, IO, Tuple, Optional, List

from makefun import wraps, remove_signature_parameters, add_signature_parameters

import nox
from nox.sessions import Session


nox_logger = logging.getLogger("nox")


PY27, PY35, PY36, PY37, PY38, PY39, PY310 = "2.7", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10"
DONT_INSTALL = "dont_install"


def power_session(
        func=None,
        envs=None,
        grid_param_name="env",
        python=None,
        py=None,
        reuse_venv=None,
        name=None,
        venv_backend=None,
        venv_params=None,
        logsdir=None,
        **kwargs
):
    """A nox.session on steroids

    :param func:
    :param envs: a dictionary {key: dict_of_params} where key is either the python version of a tuple (python version,
        grid id) and all keys in the dict_of_params must be the same in all entries. The decorated function should
        have one parameter for each of these keys, they will be injected with the value.
    :param grid_param_name: when the key in `envs` is a tuple, this name will be the name of the generated parameter to
        iterate through the various combinations for each python version.
    :param python:
    :param py:
    :param reuse_venv:
    :param name:
    :param venv_backend:
    :param venv_params:
    :param logsdir:
    :param kwargs:
    :return:
    """
    if func is not None:
        return power_session()(func)
    else:
        def combined_decorator(f):
            # replace Session with PowerSession
            f = with_power_session(f)

            # open a log file for the session, use it to stream the commands stdout and stderrs,
            # and possibly inject the log file in the session function
            if logsdir is not None:
                f = with_logfile(logs_dir=logsdir)(f)

            # decorate with @nox.session and possibly @nox.parametrize to create the grid
            return nox_session_with_grid(python=python, py=py, envs=envs, reuse_venv=reuse_venv, name=name,
                                         grid_param_name=grid_param_name, venv_backend=venv_backend,
                                         venv_params=venv_params, **kwargs)(f)

        return combined_decorator


def with_power_session(f=None):
    """ A decorator to patch the session objects in order to add all methods from Session2"""

    if f is not None:
        return with_power_session()(f)

    def _decorator(f):
        @wraps(f)
        def _f_wrapper(**kwargs):
            # patch the session arg
            PowerSession.patch(kwargs['session'])

            # finally execute the session
            return f(**kwargs)

        return _f_wrapper

    return _decorator


class PowerSession(Session):
    """
    Our nox session improvements
    """

    # ------------ commandline runners -----------

    def run2(self,
             command: Union[Iterable[str], str],
             logfile: Union[bool, str, Path] = True,
             **kwargs):
        """
        An improvement of session.run that is able to

         - automatically split the provided command if it is a string
         - use a log file

        :param command:
        :param logfile: None/False (normal nox behaviour), or True (using nox file handler), or a file path.
        :param kwargs:
        :return:
        """
        if isinstance(command, str):
            command = command.split(' ')

        self.run(*command, logfile=logfile, **kwargs)

    def run_multi(self,
                  cmds: str,
                  logfile: Union[bool, str, Path] = True,
                  **kwargs):
        """
        An improvement of session.run that is able to

         - support multiline strings
         - use a log file

        :param cmds:
        :param logfile: None/False (normal nox behaviour), or True (using nox file handler), or a file path.
        :param kwargs:
        :return:
        """
        for cmdline in (line for line in cmds.splitlines() if line):
            self.run2(cmdline, logfile=logfile, **kwargs)

    # ------------ requirements installers -----------

    def install_reqs(
            self,
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
            self.install_any("pyproject.toml#build-system", toml_setup_reqs,
                             use_conda_for=toml_use_conda_for, versions_dct=versions_dct)

        # Read test requirements from setup.cfg
        setup_cfg = read_setuptools_cfg()
        if setup:
            self.install_any("setup.cfg#setup_requires", setup_cfg.setup_requires,
                             use_conda_for=toml_use_conda_for, versions_dct=versions_dct)
        if install:
            self.install_any("setup.cfg#install_requires", setup_cfg.install_requires,
                             use_conda_for=toml_use_conda_for, versions_dct=versions_dct)
        if tests:
            self.install_any("setup.cfg#tests_requires", setup_cfg.tests_requires,
                             use_conda_for=toml_use_conda_for, versions_dct=versions_dct)

        for extra in extras:
            self.install_any("setup.cfg#extras_require#%s" % extra, setup_cfg.extras_require[extra],
                             use_conda_for=toml_use_conda_for, versions_dct=versions_dct)

        if phase is not None:
            self.install_any(phase, phase_reqs, use_conda_for=toml_use_conda_for, versions_dct=versions_dct)

    def install_any(self,
                    phase_name: str,
                    pkgs: Sequence[str],
                    use_conda_for: Sequence[str] = (),
                    versions_dct: Dict[str, str] = None,
                    logfile: Union[bool, str, Path] = True,
                    ):
        """Install the `pkgs` provided with `session.install(*pkgs)`, except for those present in `use_conda_for`"""

        nox_logger.debug("\nAbout to install *%s* requirements: %s.\n "
                         "Conda pkgs are %s" % (phase_name, pkgs, use_conda_for))

        # use the provided versions dictionary to update the versions
        if versions_dct is None:
            versions_dct = dict()
        pkgs = [pkg + versions_dct.get(pkg, "") for pkg in pkgs if versions_dct.get(pkg, "") != DONT_INSTALL]

        # install on conda... if the session uses conda backend
        if not isinstance(self.virtualenv, nox.virtualenv.CondaEnv):
            conda_pkgs = []
        else:
            conda_pkgs = [pkg_req for pkg_req in pkgs if any(get_req_pkg_name(pkg_req) == c for c in use_conda_for)]
            if len(conda_pkgs) > 0:
                nox_logger.info("[%s] Installing requirements with conda: %s" % (phase_name, conda_pkgs))
                self.conda_install2(*conda_pkgs, logfile=logfile)

        pip_pkgs = [pkg_req for pkg_req in pkgs if pkg_req not in conda_pkgs]
        # safety: make sure that nothing went modified or forgotten
        assert set(conda_pkgs).union(set(pip_pkgs)) == set(pkgs)
        if len(pip_pkgs) > 0:
            nox_logger.info("[%s] Installing requirements with pip: %s" % (phase_name, pip_pkgs))
            self.install2(*pip_pkgs, logfile=logfile)

    def conda_install2(self,
                       *conda_pkgs,
                       logfile: Union[bool, str, Path] = True,
                       **kwargs
                       ):
        """
        Same as session.conda_install() but with support for `logfile`.

        :param conda_pkgs:
        :param logfile: None/False (normal nox behaviour), or True (using nox file handler), or a file path.
        :return:
        """
        return self.conda_install(*conda_pkgs, logfile=logfile, **kwargs)

    def install2(self,
                 *pip_pkgs,
                 logfile: Union[bool, str, Path] = True,
                 **kwargs
                 ):
        """
        Same as session.install() but with support for `logfile`.

        :param pip_pkgs:
        :param logfile: None/False (normal nox behaviour), or True (using nox file handler), or a file path.
        :return:
        """
        return self.install(*pip_pkgs, logfile=logfile, **kwargs)

    def get_session_id(self):
        """Return the session id"""
        return Path(self.bin).name

    @classmethod
    def is_power_session(cls, session: Session):
        return PowerSession.install2.__name__ in session.__dict__

    @classmethod
    def patch(cls, session: Session):
        """
        Add all methods from this class to the provided object.
        Note that we could instead have created a proper proxy... but complex for not a lot of benefit.
        :param session:
        :return:
        """
        if not cls.is_power_session(session):
            for m_name, m in cls.__dict__.items():
                if not isfunction(m):
                    continue
                if m is cls.patch:
                    continue
                if not hasattr(session, m_name):
                    setattr(session.__class__, m_name, m)

        return True


# ------------- requirements related


def read_pyproject_toml():
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
        conda_pkgs = pyproject['tool']['conda']['conda_packages']
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


# ------------- log related


def with_logfile(logs_dir: Path,
                 logfile_arg: str = "logfile",
                 logfile_handler_arg: str = "logfilehandler"
                 ):
    """ A decorator to inject a logfile"""

    def _decorator(f):
        # check the signature of f
        foo_sig = signature(f)
        needs_logfile_injection = logfile_arg in foo_sig.parameters
        needs_logfilehandler_injection = logfile_handler_arg in foo_sig.parameters

        # modify the exposed signature if needed
        new_sig = None
        if needs_logfile_injection:
            new_sig = remove_signature_parameters(foo_sig, logfile_arg)
        if needs_logfilehandler_injection:
            new_sig = remove_signature_parameters(foo_sig, logfile_handler_arg)

        @wraps(f, new_sig=new_sig)
        def _f_wrapper(**kwargs):
            # find the session arg
            session = kwargs['session']  # type: Session

            # add file handler to logger
            logfile = logs_dir / ("%s.log" % PowerSession.get_session_id(session))
            error_logfile = logfile.with_name("ERROR_%s" % logfile.name)
            success_logfile = logfile.with_name("SUCCESS_%s" % logfile.name)
            # delete old files if present
            for _f in (logfile, error_logfile, success_logfile):
                if _f.exists():
                    _f.unlink()

            # add a FileHandler to the logger
            logfile_handler = log_to_file(logfile)

            # inject the log file / log file handler in the args:
            if needs_logfile_injection:
                kwargs[logfile_arg] = logfile
            if needs_logfilehandler_injection:
                kwargs[logfile_handler_arg] = logfile_handler

            # finally execute the session
            try:
                res = f(**kwargs)
            except Exception as e:
                # close and detach the file logger and rename as ERROR_....log
                remove_file_logger()
                logfile.rename(error_logfile)
                raise e
            else:
                # close and detach the file logger and rename as SUCCESS_....log
                remove_file_logger()
                logfile.rename(success_logfile)
                return res

        return _f_wrapper

    return _decorator


def log_to_file(file_path: Union[str, Path]
                ):
    """
    Closes and removes all file handlers from the nox logger,
    and add a new one to the provided file path

    :param file_path:
    :return:
    """
    for h in list(nox_logger.handlers):
        if isinstance(h, logging.FileHandler):
            h.close()
            nox_logger.removeHandler(h)
    fh = logging.FileHandler(str(file_path), mode='w')
    nox_logger.addHandler(fh)
    return fh


def get_current_logfile_handler():
    """
    Returns the current unique log file handler (see `log_to_file`)
    """
    for h in list(nox_logger.handlers):
        if isinstance(h, logging.FileHandler):
            return h
    return None


def get_log_file_stream():
    """
    Returns the output stream for the current log file handler if any (see `log_to_file`)
    """
    h = get_current_logfile_handler()
    if h is not None:
        return h.stream
    return None


def remove_file_logger():
    """
    Closes and detaches the current logfile handler
    :return:
    """
    h = get_current_logfile_handler()
    if h is not None:
        h.close()
        nox_logger.removeHandler(h)


# ------------ environment grid / parametrization related

def nox_session_with_grid(python = None,
                          py = None,
                          envs: Mapping[str, Mapping[str, Any]] = None,
                          reuse_venv: Optional[bool] = None,
                          name: Optional[str] = None,
                          venv_backend: Any = None,
                          venv_params: Any = None,
                          grid_param_name: str = None,
                          **kwargs
                          ):
    """
    Since nox is not yet capable to define a build matrix with python and parameters mixed in the same parametrize
    this implements it with a dirty hack.
    To remove when https://github.com/theacodes/nox/pull/404 is complete

    :param envs:
    :param env_python_key:
    :return:
    """
    if envs is None:
        # Fast track default to @nox.session
        return nox.session(python=python, py=py, reuse_venv=reuse_venv, name=name, venv_backend=venv_backend,
                           venv_params=venv_params, **kwargs)
    else:
        # Current limitation : session param names can be 'python' or 'py' only
        if py is not None or python is not None:
            raise ValueError("`python` session argument can not be provided both directly and through the "
                             "`env` with `session_param_names`")

    # First examine the env and collect the parameter values for python
    all_python = []
    all_params = []

    env_contents_names = None
    has_parameter = None
    for env_id, env_params in envs.items():
        # consistency checks for the env_id
        if has_parameter is None:
            has_parameter = isinstance(env_id, tuple)
        else:
            if has_parameter != isinstance(env_id, tuple):
                raise ValueError("All keys in env should be tuples, or not be tuples. Error for %r" % env_id)

        # retrieve python version and parameter
        if not has_parameter:
            if env_id not in all_python:
                all_python.append(env_id)
        else:
            if len(env_id) != 2:
                raise ValueError("Only a size-2 tuple can be used as env id")
            py_id, param_id = env_id
            if py_id not in all_python:
                all_python.append(py_id)
            if param_id not in all_params:
                all_params.append(param_id)

        # consistency checks for the dict contents.
        if env_contents_names is None:
            env_contents_names = set(env_params.keys())
        else:
            if env_contents_names != set(env_params.keys()):
                raise ValueError("Environment %r parameters %r does not match parameters in the first environment: %r"
                                 % (env_id, env_contents_names, set(env_params.keys())))

    if has_parameter and not grid_param_name:
        raise ValueError("You must provide a grid parameter name when the env keys are tuples.")

    def _decorator(f):
        s_name = name if name is not None else f.__name__
        for pyv, _param in product(all_python, all_params):
            if (pyv, _param) not in envs:
                # create a dummy folder to avoid creating a useless venv ?
                env_dir = Path(".nox") / ("%s-%s-%s-%s" % (s_name, pyv.replace('.', '-'), grid_param_name, _param))
                env_dir.mkdir(parents=True, exist_ok=True)

        # check the signature of f
        foo_sig = signature(f)
        missing = env_contents_names - set(foo_sig.parameters)
        if len(missing) > 0:
            raise ValueError("Session function %r does not contain environment parameter(s) %r" % (f.__name__, missing))

        # modify the exposed signature if needed
        new_sig = None
        if len(env_contents_names) > 0:
            new_sig = remove_signature_parameters(foo_sig, *env_contents_names)

        if has_parameter:
            if grid_param_name in foo_sig.parameters:
                raise ValueError("Internal error, this parameter has a reserved name: %r" % grid_param_name)
            else:
                new_sig = add_signature_parameters(new_sig, last=(grid_param_name,))

        @wraps(f, new_sig=new_sig)
        def _f_wrapper(**kwargs):
            # find the session arg
            session = kwargs['session']    # type: Session

            # get the versions to use for this environment
            try:
                if has_parameter:
                    grid_param = kwargs.pop(grid_param_name)
                    params_dct = envs[(session.python, grid_param)]
                else:
                    params_dct = envs[session.python]
            except KeyError:
                # Skip this session, it is a dummy one
                nox_logger.warning(
                    "Skipping configuration, this is not supported in python version %r" % session.python)
                return

            # inject the parameters in the args:
            kwargs.update(params_dct)

            # finally execute the session
            return f(**kwargs)

        if has_parameter:
            _f_wrapper = nox.parametrize(grid_param_name, all_params)(_f_wrapper)

        _f_wrapper = nox.session(python=all_python, reuse_venv=reuse_venv, name=name,
                                 venv_backend=venv_backend, venv_params=venv_params)(_f_wrapper)
        return _f_wrapper

    return _decorator


# ----------- other goodies


def rm_file(folder: Union[str, Path]
            ):
    """Since on windows Path.unlink throws permission error sometimes, os.remove is preferred."""
    if isinstance(folder, str):
        folder = Path(folder)

    if folder.exists():
        os.remove(str(folder))
        # Folders.site.unlink()  --> possible PermissionError


def rm_folder(folder: Union[str, Path]
              ):
    """Since on windows Path.unlink throws permission error sometimes, shutil is preferred."""
    if isinstance(folder, str):
        folder = Path(folder)

    if folder.exists():
        shutil.rmtree(str(folder))
        # Folders.site.unlink()  --> possible PermissionError


# --- the patch of popen able to tee to logfile --


import nox.popen as nox_popen_module
orig_nox_popen = nox_popen_module.popen


class LogFileStreamCtx:
    def __init__(self, logfile_stream):
        self.logfile_stream = logfile_stream

    def __enter__(self):
        return self.logfile_stream

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def patched_popen(
    args: Sequence[str],
    env: Mapping[str, str] = None,
    silent: bool = False,
    stdout: Union[int, IO] = None,
    stderr: Union[int, IO] = subprocess.STDOUT,
    logfile: Union[bool, str, Path] = None,
    **kwargs
) -> Tuple[int, str]:
    """
    Our patch of nox.popen.popen().

    Current behaviour in `nox` is

     - when `silent=True` (default), process err is redirected to STDOUT and process out is captured in a PIPE and sent
       to the logger (that does not displaying it :) )

     - when `silent=False` (explicitly set, or when nox is run with verbose flag), process out and process err are both
       redirected to STDOUT.

    Our implementation allows us to be a little more flexible:

     - if logfile is True or a string/Path, both process err and process out are both TEE-ed to logfile
     - at the same time, the above behaviour remains.

    :param args:
    :param env:
    :param silent:
    :param stdout:
    :param stderr:
    :param logfile: None/False (normal nox behaviour), or True (using nox file handler), or a file path.
    :return:
    """
    logfile_stream = get_log_file_stream()

    if logfile in (None, False) or (logfile is True and logfile_stream is None):
        # execute popen as usual
        return orig_nox_popen(args=args, env=env, silent=silent, stdout=stdout, stderr=stderr, **kwargs)

    else:
        # we'll need to tee the popen
        if logfile is True:
            ctx = LogFileStreamCtx
        else:
            ctx = lambda _: open(logfile, "a")

        with ctx(logfile_stream) as log_file_stream:
            if silent and stdout is not None:
                raise ValueError(
                    "Can not specify silent and stdout; passing a custom stdout always silences the commands output in "
                    "Nox's log."
                )

            shell = kwargs.get("shell", False)
            if shell:
                raise ValueError("Using shell=True is not yet supported with async streaming to log files")

            if stdout is not None or stderr is not subprocess.STDOUT:
                raise ValueError("Using custom streams is not yet supported with async popen")

            # old way
            # proc = subprocess.Popen(args, env=env, stdout=stdout, stderr=stderr)

            # New way: use asyncio to stream correctly
            # Note: if keyboard interrupts do not work we should check
            #  https://mail.python.org/pipermail/async-sig/2017-August/000374.html maybe or the following threads.

            # define the async coroutines
            async def async_popen():
                process = await asyncio.create_subprocess_exec(*args, env=env, stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE, **kwargs)

                # bind the out and err streams - see https://stackoverflow.com/a/59041913/7262247
                # to mimic nox behaviour we only use a single capturing list
                outlines = []
                await asyncio.wait([
                    # process out is only redirected to STDOUT if not silent
                    _read_stream(process.stdout, lambda l: tee(l, sinklist=outlines, sinkstream=log_file_stream,
                                                               quiet=silent, verbosepipe=sys.stdout)),
                    # process err is always redirected to STDOUT (quiet=False) with a specific label
                    _read_stream(process.stderr, lambda l: tee(l, sinklist=outlines, sinkstream=log_file_stream,
                                                               quiet=False, verbosepipe=sys.stdout, label="ERR:"))
                ])
                return_code = await process.wait()  # make sur the process has ended and retrieve its return code
                return return_code, outlines

            # run the coroutine in the event loop
            loop = asyncio.get_event_loop()
            return_code, outlines = loop.run_until_complete(async_popen())

            # just in case, flush everything
            log_file_stream.flush()
            sys.stdout.flush()
            sys.stderr.flush()

            if silent:
                # same behaviour as in nox: this will be passed to the logger, and it will act depending on verbose flag
                out = "\n".join(outlines) if len(outlines) > 0 else ""
            else:
                # already written to stdout, no need to capture
                out = ""

            return return_code, out


async def _read_stream(stream, callback):
    """Helper async coroutine to read from a stream line by line and write them in callback"""
    while True:
        line = await stream.readline()
        if line:
            callback(line)
        else:
            break


def tee(linebytes, sinklist, sinkstream, verbosepipe, quiet, label=""):
    """
    Helper routine to read a line, decode it, and append it to several sinks:

     - an optional `sinklist` list that will receive the decoded string in its "append" method
     - an optional `sinkstream` stream that will receive the decoded string in its "writelines" method
     - an optional `verbosepipe` stream that will receive only when quiet=False, the decoded string through a print

    append it to the sink, and if quiet=False, write it to pipe too.
    """
    line = linebytes.decode('utf-8').rstrip()

    if sinklist is not None:
        sinklist.append(line)

    if sinkstream is not None:
        sinkstream.write(line + "\n")
        sinkstream.flush()

    if not quiet and verbosepipe is not None:
        print(label, line, file=verbosepipe)
        verbosepipe.flush()


def patch_popen():
    nox_popen_module.popen = patched_popen

    from nox.command import popen
    if popen is not patched_popen:
        nox.command.popen = patched_popen

    # change event loop on windows
    # see https://stackoverflow.com/a/44639711/7262247
    # and https://docs.python.org/3/library/asyncio-platforms.html#subprocess-support-on-windows
    if 'win32' in sys.platform:
        # Windows specific event-loop policy & cmd
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        # cmds = [['C:/Windows/system32/HOSTNAME.EXE']]

    # loop = asyncio.ProactorEventLoop()
    # asyncio.set_event_loop(loop)


patch_popen()
