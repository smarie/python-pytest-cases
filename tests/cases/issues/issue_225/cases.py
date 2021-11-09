import pytest_cases


class MyCases:
    def case_x0(self, my_fixture):
        return 1

    def case_x1(self):
        return 1


@pytest_cases.parametrize_with_cases("c", cases=MyCases, debug=True)
def case_y(c):
    return c * 2
