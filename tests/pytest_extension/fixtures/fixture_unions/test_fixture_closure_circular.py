def test_fixture_closure_handles_circular_dependencies(pytester) -> None:
    """Test that getfixtureclosure properly handles circular dependencies.

    This test is a copy of the test in pytest 9.
    See https://github.com/pytest-dev/pytest/pull/13789/changes
    Note that the order in the fixture closure is slightly different due to the

    The test will error in the runtest phase due to the fixture loop,
    but the closure computation still completes.
    """
    pytester.makepyfile(
        """
        import pytest

        # Direct circular dependency.
        @pytest.fixture
        def fix_a(fix_b): pass

        @pytest.fixture
        def fix_b(fix_a): pass

        # Indirect circular dependency through multiple fixtures.
        @pytest.fixture
        def fix_x(fix_y): pass

        @pytest.fixture
        def fix_y(fix_z): pass

        @pytest.fixture
        def fix_z(fix_x): pass

        def test_circular_deps(fix_a, fix_x):
            pass
        """
    )
    items, _hookrec = pytester.inline_genitems()
    # assert isinstance(items[0], Function)
    fixnames = list(items[0].fixturenames)
    while fixnames[0] in ('event_loop_policy', 'environment'):
        fixnames.pop(0)
    # Note that the order changes with respect to the one in pytest :
    # We have to go depth-first
    # assert fixnames == ["fix_a", "fix_x", "fix_b", "fix_y", "fix_z"]
    assert fixnames == ["fix_a", "fix_b", "fix_x", "fix_y", "fix_z"]
