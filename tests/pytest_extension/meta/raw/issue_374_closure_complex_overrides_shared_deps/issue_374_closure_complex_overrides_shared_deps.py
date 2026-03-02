# META
# {'passed': 1, 'skipped': 0, 'failed': 0}
# END META

# This is one of the tests from https://github.com/pytest-dev/pytest/pull/13789/changes

import pytest

# Override app, but also directly use cache and settings.
# This creates multiple paths to the same fixtures.
@pytest.fixture
def app(app, cache, settings):
    pass

class TestClass:
    # Another override that uses both app and cache.
    @pytest.fixture
    def app(self, app, cache):
        pass

    def test_shared_deps(self, request, app):
        fixnames = list(request.node.fixturenames)
        while fixnames[0] in ('event_loop_policy', 'environment'):
            fixnames.pop(0)
        assert fixnames == ["request", "app", "db", "cache", "settings"]
