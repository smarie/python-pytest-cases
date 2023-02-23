from typing import Tuple

import pytest_cases


class Cases:
    ClassVar1 = int  # OK
    ClassVar2 = int  # OK
    ClassVar3 = 1  # OK
    ClassVar4 = float  # OK

    ClassVar5 = Tuple[int]  # FAILS with AttributeError: __name__
    # ClassVar6 = Tuple[float]  # FAILS  with AttributeError: __name__
    # ClassVar7 = List[int]  # FAILS with AttributeError: __name__
    # ClassVar8 = Any  # FAILS with AttributeError: __name__
    # ClassVar9 = Dict[int, str]  # FAILS with AttributeError: __name__

    def case_b(self):
        return 1


@pytest_cases.parametrize_with_cases("case", Cases)
def test_something(case) -> None:
    pass
