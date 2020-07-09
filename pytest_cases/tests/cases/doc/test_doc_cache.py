from pytest_cases import parametrize, parametrize_with_cases, fixture


already_read = set()


@parametrize(a=range(2))
def case_dummy(a):
    global already_read
    if a in already_read:
        raise ValueError()
    else:
        already_read.add(a)
        return a


@fixture(scope='session')
@parametrize_with_cases("a", cases='.')
def cached_a(a):
    return a


@parametrize(d=range(2))
def test_caching(cached_a, d):
    assert d < 2
    assert 0 <= cached_a <= 1


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_caching[dummy-a=0-d=0]',
        'test_caching[dummy-a=0-d=1]',
        'test_caching[dummy-a=1-d=0]',
        'test_caching[dummy-a=1-d=1]'
    ]
