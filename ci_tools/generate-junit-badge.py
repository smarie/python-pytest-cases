import sys
from math import floor

try:
    # python 3
    from urllib.parse import quote_plus
except ImportError:
    # python 2
    from urllib import quote_plus

import requests
import shutil
from os import makedirs, path
import xunitparser


class TestStats(object):
    def __init__(self, success_percentage, success, runned, skipped, errors):
        self.success_percentage = success_percentage
        self.success = success
        self.runned = runned
        self.skipped = skipped
        self.errors = errors


def get_test_stats(junit_xml='reports/junit/junit.xml'  # type: str
                   ):
    # type: (...) -> TestStats
    """
    read the junit test file and extract the success percentage
    :param junit_xml: the junit xml file path
    :return: the success percentage (an int)
    """
    ts, tr = xunitparser.parse(open(junit_xml))
    skipped = len(tr.skipped)
    runned = tr.testsRun - skipped
    failed = len(tr.failures)
    errors = len(tr.errors)
    success = runned - failed

    if runned > 0:
        success_percentage = floor(success * 100 / (runned + errors))
    else:
        success_percentage = 100

    return TestStats(success_percentage, success, runned, skipped, errors)


def download_badge(test_stats,                   # type: TestStats
                   dest_folder='reports/junit',  # type: str
                   badge_name='junit-badge.svg'  # type: str
                   ):
    """
    Downloads the badge corresponding to the provided success percentage, from https://img.shields.io.

    :param test_stats:
    :param dest_folder:
    :return:
    """
    if not path.exists(dest_folder):
        makedirs(dest_folder)  # , exist_ok=True) not python 2 compliant

    if test_stats.success_percentage < 50:
        color = 'red'
    elif test_stats.success_percentage < 75:
        color = 'orange'
    elif test_stats.success_percentage < 90:
        color = 'green'
    else:
        color = 'brightgreen'

    left_txt = "tests"
    # right_txt = "%s%%" % test_stats.success_percentage
    right_txt = "%s/%s" % (test_stats.success, (test_stats.runned + test_stats.errors))
    url = 'https://img.shields.io/badge/%s-%s-%s.svg' % (left_txt, quote_plus(right_txt), color)

    dest_file = path.join(dest_folder, badge_name)

    print('Generating junit badge from : ' + url)
    response = requests.get(url, stream=True)
    with open(dest_file, 'wb') as out_file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, out_file)
    del response


if __name__ == "__main__":
    # Execute only if run as a script.
    # Check the arguments
    nbargs = len(sys.argv[1:])
    if nbargs < 1:
        raise ValueError("a mandatory argument is required: <threshold>, and an optional: <dest_folder>")
    else:
        threshold = float(sys.argv[1])
        if nbargs < 2:
            dest_folder = None
        elif nbargs < 3:
            dest_folder = sys.argv[2]
        else:
            raise ValueError("too many arguments received: 2 maximum (<threshold>, <dest_folder>)")

    # First retrieve the success percentage from the junit xml
    test_stats = get_test_stats(junit_xml='%s/junit.xml' % ('reports/junit' if dest_folder is None else dest_folder))

    # Validate against the threshold
    print("Success percentage is %s%%. Checking that it is >= %s" % (test_stats.success_percentage, threshold))
    if test_stats.success_percentage < threshold:
        raise Exception("Success percentage %s%% is strictly lower than required threshold %s%%"
                        "" % (test_stats.success_percentage, threshold))

    # Download the badge
    download_badge(test_stats, dest_folder=dest_folder)
