# META
# {'passed': 2, 'skipped': 0, 'failed': 0}
# END META

import pytest


@pytest.fixture
def db():
    return 2


@pytest.fixture
def app(db):
    return 1 + db


# See https://github.com/pytest-dev/pytest/issues/13773
# Issue occurred in collection with Pytest 9+


class TestOverrideWithParent:
    # Overrides module-level app, doesn't request `db` directly, only transitively.
    @pytest.fixture
    def app(self, app):
        return 1 + app

    def test_something(self, app):
        assert app == 4  # not 3: intermediate fixture was indeed used


class TestOverrideWithoutParent:
    # Overrides module-level app, doesn't request `db` at all.
    @pytest.fixture
    def app(self):
        return 1

    def test_something(self, app):
        assert app == 1  # not 3 not 4
