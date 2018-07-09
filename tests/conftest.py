from factory import Faker
import pytest


@pytest.fixture
def requests_mock():
    import requests_mock
    # case-sensitive ensures query params are not lowercased when recording call
    # history. this is a weird side-effect of requests_mock's implementation
    # https://requests-mock.readthedocs.io/en/latest/knownissues.html#case-insensitive  # noqa
    with requests_mock.mock(case_sensitive=True) as m:
        yield m


@pytest.fixture(scope='session')
def faker():
    """
    Fixture to return a primed and ready Faker instance to generate on-the-spot
    random data
    """
    return Faker._get_faker()