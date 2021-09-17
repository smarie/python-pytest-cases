from pytest_cases import parametrize_with_cases


class FooCases:

    def case_None(self, tmpdir):
        return 1

    def case_True(self, tmpdir):
        return 1

    def case_False(self, tmpdir):
        return 1


@parametrize_with_cases("foo", cases=FooCases)
def test_issue_230(foo):
    pass
