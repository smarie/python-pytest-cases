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
    def __init__(self, success_percentage, success, runned, skipped):
        self.success_percentage = success_percentage
        self.success = success
        self.runned = runned
        self.skipped = skipped


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
    success = runned - failed

    success_percentage = floor(success * 100 / runned)

    return TestStats(success_percentage, success, runned, skipped)


def download_badge(test_stats,                  # type: TestStats
                   dest_folder='reports/junit'  # type: str
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
    right_txt = "%s/%s" % (test_stats.success, test_stats.runned)
    url = 'https://img.shields.io/badge/%s-%s-%s.svg' % (left_txt, quote_plus(right_txt), color)

    dest_file = path.join(dest_folder, 'junit-badge.svg')

    print('Generating junit badge from : ' + url)
    response = requests.get(url, stream=True)
    with open(dest_file, 'wb') as out_file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, out_file)
    del response


if __name__ == "__main__":
    # Execute only if run as a script.
    # Check the arguments
    assert len(sys.argv[1:]) == 1, "a single mandatory argument is required: <threshold>"
    threshold = float(sys.argv[1])

    # First retrieve the success percentage from the junit xml
    test_stats = get_test_stats()

    # Validate against the threshold
    print("Success percentage is %s%%. Checking that it is >= %s" % (test_stats.success_percentage, threshold))
    if test_stats.success_percentage < threshold:
        raise Exception("Success percentage %s%% is strictly lower than required threshold %s%%"
                        "" % (test_stats.success_percentage, threshold))

    # Download the badge
    download_badge(test_stats)
