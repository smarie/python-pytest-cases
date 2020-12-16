from pytest_cases import parametrize, parametrize_with_cases, case, get_case_id


def case_hello():
    return "hello !"


@case(id="hello_world")
def case_basic2():
    return "hello, world !"


@case(id="hello_name")
@parametrize("name", ["you", "earthling"])
def case_basic3(name):
    return "hello, %s !" % name


def myidgen(case_fun):
    """Custom generation of test case id"""
    return "#%s#" % get_case_id(case_fun)


@parametrize_with_cases("msg", cases=".", ids=myidgen)
def test_foo(msg):
    print(msg)


def test_synthesis(module_results_dct):
    assert list(module_results_dct) == [
        'test_foo[#hello#]',
        'test_foo[#hello_world#]',
        'test_foo[#hello_name#-you]',
        'test_foo[#hello_name#-earthling]'
    ]
