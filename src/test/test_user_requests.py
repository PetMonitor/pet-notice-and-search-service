import json
from http import HTTPStatus
from src.test.test_pet_requests import TEST_USER
from src.main.resources.user import User, Users

DATABASE_URL = "http://127.0.0.1:8000/users"

TEST_USERS = [{
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}]

TEST_USERS_OUTPUT = [{
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}]

RESPONSE_BODY_IDX = 0
RESPONSE_STATUS_IDX = 1

def test_get_users_returns_all_users(requests_mock):
    requests_mock.get(DATABASE_URL, json=TEST_USERS)
    response = Users().get()
    responseBody = response[RESPONSE_BODY_IDX]

    # Verify response content 
    assert len(responseBody) == len(TEST_USERS)
    for i in range(len(TEST_USERS)):
        assert json.dumps(responseBody[i], sort_keys=True) == json.dumps(TEST_USERS_OUTPUT[i], sort_keys=True)
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK


def test_get_user_by_id_returns_requested_user(requests_mock):
    requests_mock.get(DATABASE_URL + '/' + TEST_USERS[0]['uuid'], json=TEST_USERS[0])
    response = User().get(TEST_USERS[0]['uuid'])
    user = response[RESPONSE_BODY_IDX]
    # Verify response content 
    assert len(user) == len(TEST_USERS_OUTPUT[0])
    assert json.dumps(user, sort_keys=True) == json.dumps(TEST_USERS_OUTPUT[0], sort_keys=True)
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK