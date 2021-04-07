def test_foo(dummy_fixture):
    """Before the fix this test would not even start because a conftest loading error was appearing"""
    assert dummy_fixture == 2
