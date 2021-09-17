from pytest_cases import parametrize_with_cases


class FooCases:
    def case_1(self):
        return 1

    class SubFooCases:
        def case_2(self):
            return 2

        class SubSubFooCases:
            def case_3(self):
                return 3

    def case_3(self):  # duplicate name; on purpose
        return 3


@parametrize_with_cases("x", FooCases)
def test_foo(x):
    test_foo.received.append(x)


test_foo.received = []


@parametrize_with_cases("x", FooCases.SubFooCases)
def test_subfoo(x):
    test_subfoo.received.append(x)


test_subfoo.received = []


def test_class_with_nested_uses_nested():
    assert test_foo.received == [1, 2, 3, 3]


def test_direct_nested_class_reference_works():
    assert test_subfoo.received == [2, 3]
