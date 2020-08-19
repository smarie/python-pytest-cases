def case_a(b, a):
    # a and b are fixtures defined in caller module/class
    # note that case id is also 'a'. The goal is to check that no conflict happens here
    assert a in (1, 2)
    assert b == -1
    return 'case!'
