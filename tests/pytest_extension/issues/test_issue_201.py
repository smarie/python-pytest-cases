from pytest_cases import fixture, parametrize_with_cases, unpack_fixture


class Cases:
    def case_one(self):
        return "/", {"param": "value"}


@fixture
@parametrize_with_cases("case", Cases)
def case(case):
    return case


class TestAPIView(object):
    url, data = unpack_fixture("url, data", case, in_cls=True)

    def test_foo(self, url, data):
        assert url == "/"
        assert data == {"param": "value"}
