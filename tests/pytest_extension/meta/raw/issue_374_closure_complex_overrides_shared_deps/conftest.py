import pytest

@pytest.fixture
def db():
    pass


@pytest.fixture
def cache():
    pass


@pytest.fixture
def settings():
    pass


@pytest.fixture
def app(db, cache, settings):
    pass
