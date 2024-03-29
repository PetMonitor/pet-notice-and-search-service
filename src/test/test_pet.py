import json
from http import HTTPStatus
from src.main.resources.pet import UserPet, UserPets


TEST_USER = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "_ref": "e6ebed0b-803c-43be-baaf-d370bc4e07f0",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}

TEST_PETS = [
    {
        "uuid": "123e4567-e89b-12d3-a456-426614174001",
        "_ref": "578ac850-27d1-4e6e-8cb0-d0bd7219a69d",
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
        "_ref": "08ea7708-204e-4836-bd49-5f869e731971",
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

TEST_PETS_OUTPUT = [
    {
        "petId": "123e4567-e89b-12d3-a456-426614174001",
        "_ref": "578ac850-27d1-4e6e-8cb0-d0bd7219a69d",
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
        "petId": "123e4567-e89b-12d3-a456-426614174003",
        "_ref": "08ea7708-204e-4836-bd49-5f869e731971",
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

DATABASE_URL = "http://127.0.0.1:8000/users/" + TEST_USER["uuid"] + "/pets"

def test_get_pets_returns_all_pets(requests_mock):
    requests_mock.get(DATABASE_URL, json=TEST_PETS)
    response = UserPets().get(TEST_USER['uuid'])
    responseBody = response[RESPONSE_BODY_IDX]
    print("Response body {}".format(json.dumps(responseBody)))
    
    # Verify response content 
    assert len(responseBody) == len(TEST_PETS)
    for i in range(len(TEST_PETS)):
        assert json.dumps(responseBody[i], sort_keys=True) == json.dumps(TEST_PETS_OUTPUT[i], sort_keys=True)
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK


def test_get_pet_by_id_returns_requested_pet(requests_mock):
    petId = TEST_PETS[0]['uuid']
    requests_mock.get(DATABASE_URL + '/' + petId, json=TEST_PETS[0])
    response = UserPet().get(TEST_USER['uuid'], petId)
    pet = response[RESPONSE_BODY_IDX]    
    # Verify response content 
    assert len(pet) == len(TEST_PETS_OUTPUT[0])
    assert json.dumps(pet) == json.dumps(TEST_PETS_OUTPUT[0])
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK

def test_delete_pet_returns_ok(requests_mock):
    petId = TEST_PETS[0]['uuid']

    requests_mock.delete(DATABASE_URL + '/' + petId, json=[1])
    response = UserPet().delete(TEST_USER['uuid'], petId)

    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK
    assert response[RESPONSE_BODY_IDX] == "Correctly deleted [1] records"

#TODO add post test
#TODO add put test   
