import requests
import shutil
from os import makedirs, path
import xunitparser


def download_badge(junit_xml: str='reports/junit/junit.xml', dest_folder: str='reports/junit'):

    makedirs(dest_folder, exist_ok=True)

    # read the junit test file
    ts, tr = xunitparser.parse(open(junit_xml))
    runned = tr.testsRun
    failed = len(tr.failures)

    success_percentage = round((runned - failed) * 100 / runned)
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
    # execute only if run as a script
    download_badge()