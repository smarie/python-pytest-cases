# META
# {'passed': 1, 'skipped': 0, 'failed': 0}
# END META

# This is one of the tests from https://github.com/pytest-dev/pytest/pull/13789/changes

import pytest

@pytest.fixture
def fix1(fix2): pass

@pytest.fixture
def fix2(fix3): pass

@pytest.fixture
def fix3(): pass

@pytest.mark.parametrize('fix2', ['2'])
def test_it(request, fix1):
    for fixnames in list(request.node.fixturenames), list(request.fixturenames):
        # Remove extra fixtures from plugins, that should be at the beginning
        while fixnames[0] in ('event_loop_policy', 'environment'):
            fixnames.pop(0)
        assert fixnames == ["request", "fix1", "fix2"]
