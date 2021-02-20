from pytest_cases import filters, case, parametrize_with_cases

A = "a"
B = "b"
C = "c"


@case(tags=[A])
def case_one():
    return 1


@case(tags=[A, B])
def case_two():
    return 2


@case(tags=[B, C])
def case_three():
    return 3


@case(tags=[A, C])
def case_four():
    return 4


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_tag(B)
)
def test_filter_with_tag(value):
    print(value)


@parametrize_with_cases(
    argnames="value", cases=".", filter=~filters.has_tag(B)
)
def test_filter_without_tag(value):
    print(value)


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_tag(B) & filters.has_tag(C)
)
def test_filter_with_and_relation(value):
    print(value)


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_tag(B) | filters.has_tag(C)
)
def test_filter_with_or_relation(value):
    print(value)


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_prefix("case_t")
)
def test_filter_with_prefix(value):
    print(value)


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_suffix("e")
)
def test_filter_with_suffix(value):
    print(value)
