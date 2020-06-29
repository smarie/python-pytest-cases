from pytest_harvest import get_session_synthesis_dct

from pytest_cases import parametrize_with_cases, parametrize


class CasesFoo:
    def case_hello(self):
        return "hello world"

    @parametrize(who=('you', 'there'))
    def case_simple_generator(self, who):
        return "hello %s" % who


@parametrize_with_cases("msg", cases='.')
def test_foo(msg):
    assert isinstance(msg, str) and msg.startswith("hello")


def test_foo_synthesis(request):
    results_dct = get_session_synthesis_dct(request, filter=test_foo, test_id_format='function')
    assert list(results_dct) == [
        'test_foo[hello]',
        'test_foo[simple_generator-who=you]',
        'test_foo[simple_generator-who=there]'
    ]
