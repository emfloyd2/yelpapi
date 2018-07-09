import time

from requests_mock.adapter import ANY
import pytest
from pytest_localserver.http import WSGIServer
import requests

import yelpapi


TEST_SERVER_TIMEOUT = 4


def hung_app(environ, start_response):
    """
    This app will simulate a hung API request (something that has run longer
    than we expect).
    """
    # Picking an arbitrarily long value, don't want to rely on default of YelpAPI
    # class (wait forever) - just in case the default ever changes from None
    time.sleep(TEST_SERVER_TIMEOUT)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Dummy Response!\n']


@pytest.fixture
def hung_server(request):
    """WSGI server for our hung app"""
    server = WSGIServer(application=hung_app)
    server.start()
    request.addfinalizer(server.stop)
    return server


class TestTimeout(object):
    """Collection of tests to verify timeout logic"""

    def test_default_timeout(self, mocker, faker, requests_mock):
        """Verify that default is passed into :meth:`requests.Session.get`"""
        requests_mock.request(ANY, ANY, json={})
        mocked_session_get = mocker.spy(
            requests.Session,
            'get',
        )
        yelp = yelpapi.yelpapi.YelpAPI(api_key=faker.pystr())
        yelp._query(faker.uri())
        assert mocked_session_get.call_args[1]['timeout'] == yelpapi.DEFAULT_TIMEOUT

    def test_timeout_override(self, mocker, faker, hung_server):
        """Verify timeout override is passed into :meth:`requests.Session.get`"""
        expected_timeout_arg = TEST_SERVER_TIMEOUT / 2
        mocked_session_get = mocker.spy(
            requests.Session,
            'get',
        )
        yelp = yelpapi.YelpAPI(api_key=faker.pystr(), timeout=expected_timeout_arg)
        with pytest.raises(requests.ReadTimeout):
            # Generate real timeout condition using the server fixture designed
            # to hang longer than specified timeout
            yelp._query(hung_server.url)
        assert mocked_session_get.call_args[1]['timeout'] == expected_timeout_arg
