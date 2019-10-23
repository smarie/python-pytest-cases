import ast
import os
import shlex
import sys
from importlib import import_module

import re
from os.path import join, dirname, pardir, isdir, exists

import pytest
from six import string_types

# Make the list of all tests that we will have to execute (each in an independent pytest runner)
THIS_DIR = dirname(__file__)
tests_raw_folder = join(THIS_DIR, 'raw')
test_files = [f for f in os.listdir(tests_raw_folder) if not f.startswith('_')]


META_REGEX = re.compile(
"""^(# META
# )(?P<asserts_dct>.*)(
# END META)
.*""")


@pytest.mark.parametrize('test_to_run', test_files, ids=str)
def test_run_all_tests(test_to_run, testdir):
    """
    This is a meta-test. It is executed for each test file in the 'raw' folder.
    For each of them, the file is retrieved and the expected test results are read from its first lines.
    Then a dedicated pytest runner is run on this file, and the results are compared with the expected ones.

    See https://docs.pytest.org/en/latest/writing_plugins.html

    :param test_to_run:
    :param testdir:
    :return:
    """
    cmdargs = []
    conf_file_path = None
    test_to_run_path = join(tests_raw_folder, test_to_run)
    if isdir(test_to_run_path):
        test_folder_path = test_to_run_path

        # check if there is a cmdargs file
        cmdargs_file_path = join(test_folder_path, "cmdargs.txt")
        if exists(cmdargs_file_path):
            with open(cmdargs_file_path) as c:
                cmdargs = c.read()
            cmdargs = process_cmdargs(cmdargs)

        # check if there is a conf file
        conf_file_path = join(test_folder_path, "conf.py")
        if exists(conf_file_path):
            with open(conf_file_path) as c:
                cfg_contents = c.read()
                # Create a temporary conftest.py file
                print("\nConfig contents: %s" % cfg_contents)
                testdir.makeconftest(cfg_contents)

        # the test file should have the same name than the dir
        test_to_run = test_to_run + ".py"
        test_to_run_path = join(test_folder_path, test_to_run)
        if not exists(test_to_run_path):
            raise ValueError("Test file %s not found in folder %s" % (test_to_run, test_folder_path))

    with open(test_to_run_path) as f:
        # create a temporary pytest test file
        test_file_contents = f.read()
        testdir.makepyfile(test_file_contents)

        # Grab the expected things to check when this is executed
        m = META_REGEX.match(test_file_contents)
        if m is None:
            raise ValueError("test file '%s' does not contain the META-header" % test_to_run)
        asserts_dct_str = m.groupdict()['asserts_dct']
        asserts_dct = ast.literal_eval(asserts_dct_str)

        # Here we run pytest
        print("\nTesting that running pytest on file %s with config file %s results in %s."
              "" % (test_to_run, conf_file_path, str(asserts_dct)))

        print("For debug, temp dir is: %s" % testdir.tmpdir)

        # protect against pycharm fiddling with the config
        from _pytest import config
        jb_prepareconfig = config._prepareconfig
        if jb_prepareconfig.__module__ != config.get_config.__module__:
            # we are in pycharm ! Fix that
            config._prepareconfig = get_pytest_prepare_config()

        # run
        # first = testdir.runpytest("--collect-only", "-p", "no:cacheprovider")  # ("-q")
        # outfirst = "\n".join(first.outlines)
        # assert "collected 1 items" in outfirst

        # ********* RUN *********
        result = testdir.runpytest(*cmdargs)  # ("-q")

        # put back the PyCharm hack
        config._prepareconfig = jb_prepareconfig

        # Here we check that everything is ok
        try:
            result.assert_outcomes(**asserts_dct)
        except Exception as e:
            err = Exception("Error while asserting that %s results in %s. Actual results: %s"
                            "" % (test_to_run, str(asserts_dct), result.parseoutcomes()))
            err.__cause__ = e
            raise err


def get_pytest_prepare_config(dynamic=False):
    import py
    import shlex
    if dynamic:
        from _pytest import config
        with open(config.__file__) as cfg_file_original:
            _capture = False
            all_lines = []
            for l in cfg_file_original.readlines():
                if l.startswith("def _prepareconfig"):
                    _capture = True
                    all_lines.append(l)
                elif _capture:
                    if l.startswith(" "):
                        all_lines.append(l)
                    else:
                        break

        from _pytest.config import get_config
        g = globals()
        l = locals()
        prepare_cfg_code = "".join(all_lines)
        # print(prepare_cfg_code)
        exec(prepare_cfg_code, l, g)
        real_prepare_config = g['_prepareconfig']

    else:
        import sys
        from _pytest.config import get_config
        def real_prepare_config(args=None, plugins=None):
            if args is None:
                args = sys.argv[1:]
            elif isinstance(args, py.path.local):
                args = [str(args)]
            elif not isinstance(args, (tuple, list)):
                if not isinstance(args, string_types):
                    raise ValueError("not a string or argument list: %r" % (args,))
                args = shlex.split(args, posix=sys.platform != "win32")
            config = get_config()
            pluginmanager = config.pluginmanager
            try:
                if plugins:
                    for plugin in plugins:
                        if isinstance(plugin, py.builtin._basestring):
                            pluginmanager.consider_pluginarg(plugin)
                        else:
                            pluginmanager.register(plugin)
                return pluginmanager.hook.pytest_cmdline_parse(
                    pluginmanager=pluginmanager, args=args)
            except BaseException:
                config._ensure_unconfigure()
                raise

    return real_prepare_config


def process_cmdargs(cmdargs):
    return shlex.split(cmdargs)
