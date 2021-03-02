from pytest_cases import filters, case, parametrize_with_cases

A = "a"
B = "b"
C = "c"


@case(tags=[A], id="tom")
def case_one():
    return 1


@case(tags=[A, B], id="tim")
def case_two():
    return 2


@case(tags=[B, C], id="toni")
def case_three():
    return 3


@case(tags=[A, C])
def case_dom():
    return 4


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_tag(B)
)
def test_filter_with_tag(value):
    pass


@parametrize_with_cases(
    argnames="value", cases=".", filter=~filters.has_tag(B)
)
def test_filter_without_tag(value):
    pass


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_tag(B) & filters.has_tag(C)
)
def test_filter_with_and_relation(value):
    pass


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_tags(B, C)
)
def test_filter_with_two_tags(value):
    pass


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.has_tag(B) | filters.has_tag(C)
)
def test_filter_with_or_relation(value):
    pass


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.id_has_prefix("t")
)
def test_filter_with_prefix(value):
    pass


@parametrize_with_cases(
    argnames="value", cases=".", filter=filters.id_has_suffix("m")
)
def test_filter_with_suffix(value):
    pass


def test_filter(module_results_dct):
    assert list(module_results_dct) == [
        'test_filter_with_tag[tim]',
        'test_filter_with_tag[toni]',
        'test_filter_without_tag[tom]',
        'test_filter_without_tag[dom]',
        'test_filter_with_and_relation[toni]',
        'test_filter_with_two_tags[toni]',
        'test_filter_with_or_relation[tim]',
        'test_filter_with_or_relation[toni]',
        'test_filter_with_or_relation[dom]',
        'test_filter_with_prefix[tom]',
        'test_filter_with_prefix[tim]',
        'test_filter_with_prefix[toni]',
        'test_filter_with_suffix[tom]',
        'test_filter_with_suffix[tim]',
        'test_filter_with_suffix[dom]'
    ]
