from pytest_cases import fixture, parametrize_with_cases


@fixture
@parametrize_with_cases('arg', cases='cases')
def function_scoped(arg):
    return [arg]

# This tests would fail with a ScopeMismatch
# during collection before #317
def test_scope_mismatch_collection(scope_mismatch):
    assert scope_mismatch == [1]

def test_scopes(session_scoped, function_scoped, class_scoped):
    session_scoped.append(2)
    function_scoped.append(2)
    class_scoped.append(2)
    assert session_scoped == [1, 2]
    assert function_scoped == [1, 2]
    assert class_scoped == [1, 2]

def test_scopes_again(session_scoped, function_scoped, class_scoped):
    session_scoped.append(3)
    function_scoped.append(3)
    class_scoped.append(3)
    assert session_scoped == [1, 2, 3]
    assert function_scoped == [1, 3]
    assert class_scoped == [1, 3]


class TestScopesInClass:

    def test_scopes_in_class(self, session_scoped,
                             function_scoped, class_scoped):
        session_scoped.append(4)
        function_scoped.append(4)
        class_scoped.append(4)
        assert session_scoped == [1, 2, 3, 4]
        assert function_scoped == [1, 4]
        assert class_scoped == [1, 4]

    def test_scopes_in_class_again(self, session_scoped,
                                   function_scoped, class_scoped):
        session_scoped.append(5)
        function_scoped.append(5)
        class_scoped.append(5)
        assert session_scoped == [1, 2, 3, 4, 5]
        assert function_scoped == [1, 5]
        assert class_scoped == [1, 4, 5]
