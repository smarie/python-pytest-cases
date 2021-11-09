from pytest_cases import parametrize, parametrize_with_cases, case, fixture


def case_hello():
    return "hello !"


@fixture
@parametrize("_name", ["you", "earthling"])
def name(_name):
    return _name


@case(id="hello_fixture")
def case_basic3(name):
    return "hello, %s !" % name


@parametrize_with_cases("msg", cases=".", idstyle="nostyle")
def test_default_idstyle(msg):
    print(msg)


@parametrize_with_cases("msg", cases=".", idstyle="compact")
def test_compact_idstyle(msg):
    print(msg)


@parametrize_with_cases("msg", cases=".", idstyle="explicit")
def test_explicit_idstyle(msg):
    print(msg)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_default_idstyle[hello]',
        'test_default_idstyle[hello_fixture-you]',
        'test_default_idstyle[hello_fixture-earthling]',
        'test_compact_idstyle[/hello]',
        'test_compact_idstyle[/hello_fixture-you]',
        'test_compact_idstyle[/hello_fixture-earthling]',
        'test_explicit_idstyle[msg/hello]',
        'test_explicit_idstyle[msg/hello_fixture-you]',
        'test_explicit_idstyle[msg/hello_fixture-earthling]'
    ]
