import json
from http import HTTPStatus
from src.main.resources.pet import UserPet, UserPets


TEST_USER = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}

TEST_PETS = [
    {
        "uuid": "123e4567-e89b-12d3-a456-426614174001",
        "userId": "123e4567-e89b-12d3-a456-426614174000",
        "type": "DOG",
        "name": "firulais",
        "furColor": "brown",
        "rightEyeColor": "black",
        "leftEyeColor": "black",
        "breed": "crossbreed",
        "size": "SMALL",
        "lifeStage": "ADULT",
        "age": 8,
        "sex": "MALE",
        "description": "a very nice dog",
        "photos": []
    },
    {
        "uuid": "123e4567-e89b-12d3-a456-426614174003",
        "userId": "123e4567-e89b-12d3-a456-426614174000",
        "type": "CAT",
        "name": "yuli",
        "furColor": "white and orange",
        "rightEyeColor": "brown",
        "leftEyeColor": "brown",
        "breed": "crossbreed",
        "size": "SMALL",
        "lifeStage": "ADULT",
        "age": 6,
        "sex": "FEMALE",
        "description": "she likes to chase mice",
        "photos": []
    }
]

RESPONSE_BODY_IDX = 0
RESPONSE_STATUS_IDX = 1

DATABASE_URL = "http://127.0.0.1:8000/users" + "/" + TEST_USER["uuid"] + "/pets"

def test_get_pets_returns_all_pets(requests_mock):
    requests_mock.get(DATABASE_URL, json=TEST_PETS)
    response = UserPets().get(TEST_USER['uuid'])
    responseBody = response[RESPONSE_BODY_IDX]
    print("Response body {}".format(json.dumps(responseBody)))

    # Assert only one user was returned
    assert len(responseBody) == len(TEST_PETS)
    # Verify response content 
    for i in range(len(TEST_PETS)):
        assert json.dumps(responseBody[i]) == json.dumps(TEST_PETS[i])
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK
