import sys

import requests
import shutil
from os import makedirs, path
import xunitparser


def get_success_percentage(junit_xml='reports/junit/junit.xml'  # type: str
                           ):
    # type: (...) -> int
    """
    read the junit test file and extract the success percentage
    :param junit_xml: the junit xml file path
    :return: the success percentage (an int)
    """
    ts, tr = xunitparser.parse(open(junit_xml))
    runned = tr.testsRun
    failed = len(tr.failures)

    success_percentage = round((runned - failed) * 100 / runned)
    return success_percentage


def download_badge(success_percentage,          # type: int
                   dest_folder='reports/junit'  # type: str
                   ):
    """
    Downloads the badge corresponding to the provided success percentage, from https://img.shields.io.

    :param success_percentage:
    :param dest_folder:
    :return:
    """
    if not path.exists(dest_folder):
        makedirs(dest_folder)  # , exist_ok=True) not python 2 compliant

    if success_percentage < 50:
        color = 'red'
    elif success_percentage < 75:
        color = 'orange'
    elif success_percentage < 90:
        color = 'green'
    else:
        color = 'brightgreen'
    url = 'https://img.shields.io/badge/tests-' + str(success_percentage) + '%25-' + color + '.svg'

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
    success_percentage = get_success_percentage()

    # Validate against the threshold
    print("Success percentage is %s%%. Checking that it is >= %s" % (success_percentage, threshold))
    if success_percentage < threshold:
        raise Exception("Success percentage %s%% is strictly lower than required threshold %s%%"
                        "" % (success_percentage, threshold))

    # Download the badge
    download_badge(success_percentage)
