import json
from http import HTTPStatus
from src.test.test_pet_requests import TEST_USER
from src.main.resources.user import User, Users
from mock import patch
from src.main.app import app

DATABASE_URL = "http://127.0.0.1:8000/users"

TEST_USERS = [{
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "_ref": "e6ebed0b-803c-43be-baaf-d370bc4e07f0",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}]

TEST_USERS_OUTPUT = [{
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "_ref": "e6ebed0b-803c-43be-baaf-d370bc4e07f0",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}]


"""
This mock classes are to override User and Users requests methods.
With the @patch decorator it is posible to make request.get() return
the next fake object; so it can perform an url check and mutate
to simulate different endpoints.
"""
class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url == DATABASE_URL):
            self.status_code = 200
            self.response = TEST_USERS
        elif (self.url == DATABASE_URL + '/' + TEST_USERS[0]['uuid']):
            self.status_code = 200
            self.response = TEST_USERS[0]
        else:
            self.status_code = 404
            self.response = {"error":"test route not found"}            

    def json(self):
        return self.response
    
    def raise_for_status(self):
        return

    def response(self):
        return self.response


class TestUserRequests(object):

    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.isRequestAuthorized", return_value=True)
    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_users_returns_all_users(self, requestAuthorizedMock, FakeGet):
        client = app.test_client()
        response = client.get('/api/v0/users')

        responseBody = json.loads(response.get_data())
        print("Test GET /users response: {}".format(str(responseBody)))

        # Verify response content 
        assert len(responseBody) == len(TEST_USERS_OUTPUT)
        for i in range(len(TEST_USERS_OUTPUT)):
            assert json.dumps(responseBody[i], sort_keys=True) == json.dumps(TEST_USERS_OUTPUT[i], sort_keys=True)
        assert response.status_code == HTTPStatus.OK


    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_user_by_id_returns_requested_user(self, requestAuthorizedMock, FakeGet):
        client = app.test_client()
        response = client.get('/api/v0/users/' + TEST_USERS[0]['uuid'])

        responseBody = json.loads(response.get_data())
        print("Test GET /users/{} response: {}".format(TEST_USERS[0]['uuid'], str(responseBody)))

        # Verify response content 
        assert len(responseBody) == len(TEST_USERS_OUTPUT[0])
        assert json.dumps(responseBody, sort_keys=True) == json.dumps(TEST_USERS_OUTPUT[0], sort_keys=True)
        assert response.status_code == HTTPStatus.OK