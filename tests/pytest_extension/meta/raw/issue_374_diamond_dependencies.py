# META
# {'passed': 1, 'skipped': 0, 'failed': 0}
# END META

# This is one of the tests from https://github.com/pytest-dev/pytest/pull/13789/changes

import pytest

@pytest.fixture
def db(): pass

@pytest.fixture
def user(db): pass

@pytest.fixture
def session(db): pass

@pytest.fixture
def app(user, session): pass

def test_diamond_deps(request, app):
    for fixnames in list(request.node.fixturenames), list(request.fixturenames):
        # Remove extra fixtures from plugins, that should be at the beginning
        while fixnames[0] in ('event_loop_policy', 'environment'):
            fixnames.pop(0)
        assert fixnames == ["request", "app", "user", "db", "session"]
