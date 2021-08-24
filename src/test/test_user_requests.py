import json
from http import HTTPStatus
from src.main.resources.user import User, Users

DATABASE_URL = "http://127.0.0.1:8000/users"

TEST_USER = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}

RESPONSE_BODY_IDX = 0
RESPONSE_STATUS_IDX = 1

def test_get_users_returns_all_users(requests_mock):
    requests_mock.get(DATABASE_URL, json=[TEST_USER])
    response = Users().get()
    responseBody = response[RESPONSE_BODY_IDX]
    # Assert only one user was returned
    assert len(responseBody) == 1
    # Get the user from the list
    user = responseBody[0]
    # Verify response content 
    assert json.dumps(user) == json.dumps(TEST_USER)
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK


def test_get_user_by_id_returns_requested_user(requests_mock):
    requests_mock.get(DATABASE_URL + '/' + TEST_USER['uuid'], json=TEST_USER)
    response = User().get(TEST_USER['uuid'])
    user = response[RESPONSE_BODY_IDX]
    assert len(user) == len(TEST_USER)
    # Verify response content 
    assert json.dumps(user) == json.dumps(TEST_USER)
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK