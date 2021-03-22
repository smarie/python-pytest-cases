import sys

if __name__ == "__main__":
    # Execute only if run as a script.
    # Check the arguments
    nbargs = len(sys.argv[1:])
    if nbargs != 1:
        raise ValueError("a mandatory argument is required: <version>")

    expected_version_str = sys.argv[1]
    try:
        expected_version = tuple(int(i) for i in expected_version_str.split("."))
    except Exception as e:
        raise ValueError("Error while parsing expected version %r: %r" % (expected_version, e))

    if len(expected_version) < 1:
        raise ValueError("At least a major is expected")

    if sys.version_info[0] != expected_version[0]:
        raise AssertionError("Major version does not match. Expected %r - Actual %r" % (expected_version_str, sys.version))

    if len(expected_version) >= 2 and sys.version_info[1] != expected_version[1]:
        raise AssertionError("Minor version does not match. Expected %r - Actual %r" % (expected_version_str, sys.version))

    if len(expected_version) >= 3 and sys.version_info[2] != expected_version[2]:
        raise AssertionError("Patch version does not match. Expected %r - Actual %r" % (expected_version_str, sys.version))

    print("SUCCESS - Actual python version %r matches expected one %r" % (sys.version, expected_version_str))
