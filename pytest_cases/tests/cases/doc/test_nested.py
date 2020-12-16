from pytest_cases import parametrize_with_cases


class FooCases:
    def case_1(self):
        return 1

    class SubFooCases:
        def case_2(self):
            return 2

    def case_3(self):
        return 3


@parametrize_with_cases("x", FooCases)
def test_foo(x):
    print(x)
