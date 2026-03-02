import pytest


@pytest.fixture
def db(): pass


@pytest.fixture
def app(db): pass


@pytest.fixture
def intermediate(app): pass