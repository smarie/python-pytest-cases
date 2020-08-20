from pytest_cases import parametrize


def case_a(b, a):
    # a and b are fixtures defined in caller module/class
    # note that case id is also 'a'. The goal is to check that no conflict happens here
    assert a in (1, 2)
    assert b == -1
    return 'case!'


@parametrize(a=('*', '**'))
def case_b(b, a):
    assert b == -1
    assert a in ('*', '**')
    return 'case!'


class CaseA:
    def case_a(self, b, a):
        # a and b are fixtures defined in caller module/class
        # note that case id is also 'a'. The goal is to check that no conflict happens here
        assert a in (1, 2)
        assert b == -1
        return 'case!'

    @parametrize(a=('*', '**'))
    def case_b(self, b, a):
        assert b == -1
        assert a in ('*', '**')
        return 'case!'
