# META
# {'passed': 1, 'skipped': 0, 'failed': 0}
# END META

# This is one of the tests from https://github.com/pytest-dev/pytest/pull/13789/changes

import pytest

from pytest_cases import fixture_union

# Overrides conftest-level `app` and requests it.
app = fixture_union("app", ["intermediate", "db"])


class TestClass:
    # Overrides module-level `app` and requests it.
    @pytest.fixture
    def app(self, app):
        pass

    def test_something(self, request, app):
        # Both dynamic and static fixture closures should include 'db'.
        assert 'db' in request.fixturenames
        assert 'db' in request.node.fixturenames
        # No dynamic dependencies, should be equal.
        assert set(request.fixturenames) == set(request.node.fixturenames)
