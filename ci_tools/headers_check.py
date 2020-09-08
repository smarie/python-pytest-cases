import re

import click
from dateutil.utils import today
from glob import glob
from os.path import dirname, join, abspath


# path to the the pytest_cases folder
root = abspath(join(dirname(__file__), '../pytest_cases'))
default_tmpl = abspath(join(dirname(__file__), 'headers.tmpl'))


@click.command()
@click.option('-s', '--single', 'single', is_flag=True)
@click.option('-r', '--remove', 'action', flag_value='remove')
@click.option('-i', '--inject', 'action', flag_value='inject', default=True)
def check_all_headers(path=root, headers_template=default_tmpl, action='inject', single=False):
    """

    :param path:
    :param headers_template:
    :param remove:
    :return:
    """
    headers_tmpl = ""
    with open(headers_template) as f:
        for line in f.readlines():
            headers_tmpl += "# %s" % line if line != "\n" else "#\n"

    # note: the year now disappeared, everything is redirected to the LICENSE file at the root
    headers_regex = re.compile(re.escape(headers_tmpl).replace("\\{", "{").replace("\\}", "}").format(year=".*"))
    headers = headers_tmpl.format(year=today().year)

    # rel_root = relpath(abspath(root), getcwd())
    for f in glob("%s/**/*.py" % path, recursive=True):
        # skip meta tests
        if "meta" in f:
            print("skipping file %s" % f)
            continue

        # read file
        with open(f, mode="rt") as contents:
            src = contents.read()

        # skip empty files
        if src.strip() == "":
            print("skipping file %s as it is empty" % f)
            continue

        if action == 'inject':
            if src.startswith(headers):
                continue
            match = headers_regex.match(src)
            if match:
                # different year. remove the existing header and re-apply
                src = src[match.end():]
            new_contents = headers + src
        elif action == 'remove':
            if src.startswith(headers):
                new_contents = src[len(headers):]
            else:
                match = headers_regex.match(src)
                if match:
                    new_contents = src[match.end():]
                else:
                    continue
        else:
            raise ValueError("invalid action: %s" % action)

        with open(f, mode="wt") as contents:
            contents.write(new_contents)

        if single:
            print("single file modded '%s' - exiting" % f)
            break


if __name__ == '__main__':
    check_all_headers()
