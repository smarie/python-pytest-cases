from collections import defaultdict

from pytest_cases import fixture, fixture_union, parametrize

used = defaultdict(lambda: False)
torn_down = defaultdict(lambda: False)


@fixture(scope='session')
def s1():
    name = 's1'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='session')
def s2():
    name = 's2'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='session')
def s3():
    name = 's3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='module')
def M1s1s2(s1, s2):
    name = 'M1s1s2'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='module')
def M2s1s3(s1, s3):
    name = 'M2s1s3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
def F1M1s1s2(M1s1s2):
    name = 'F1M1s1s2'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
@parametrize(i=[0, 1])
def F2(i):
    name = 'F2(%s)' % i
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
def F3s2s3(s2, s3):
    name = 'F3s2s3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


@fixture(scope='function')
def F4M2s1s3(M2s1s3):
    name = 'F4M2s1s3'
    global used, torn_down
    assert not used[name]
    used[name] = True
    yield name
    torn_down[name] += 1


d = fixture_union('d', (F1M1s1s2, F2, F3s2s3, F4M2s1s3))


super_closure = None


def test_foo(d, request):
    # store closure for later analysis or test
    global super_closure
    super_closure = request._pyfuncitem._fixtureinfo.names_closure


def test_synthesis(module_results_dct):
    assert all(torn_down.values())
    assert list(module_results_dct) == [
        'test_foo[d_is_F1M1s1s2]',
        'test_foo[d_is_F2-i=0]',
        'test_foo[d_is_F2-i=1]',
        'test_foo[d_is_F3s2s3]',
        'test_foo[d_is_F4M2s1s3]'
    ]

    function_scoped = ('F1M1s1s2', 'F2(0)', 'F2(1)', 'F3s2s3', 'F4M2s1s3')
    module_scoped = ('M1s1s2', 'M2s1s3')
    session_scoped = ('s1', 's2', 's3')

    for item in function_scoped + module_scoped + session_scoped:
        assert used[item] == 1, "item %s was not used once" % item

        if item in function_scoped:
            assert torn_down[item] == 1, "item %s was not torn down once" % item
        # else we know that the last module/session fixture alive is not properly torn down, this is a pytest issue


# def test_super_closure():
#     global super_closure
#     print(super_closure)
