import json
import uuid
import requests

from os import getenv
from enum import Enum, auto
from http import HTTPStatus
from cerberus import Validator
from flask_restful import fields, request, Resource, marshal_with

from src.main.constants import DATABASE_SERVER_URL


class PetType(Enum):
    DOG = auto()
    CAT = auto()


class PetSize(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()


class PetLifeStage(Enum):
    BABY = auto()
    ADULT = auto()
    SENIOR = auto()


class PetSex(Enum):
    MALE = auto()
    FEMALE = auto()


# Fields returned by the src for the Pet resource
pet_fields = {
    'petId': fields.String(attribute='uuid'),
    '_ref': fields.String,
    'userId': fields.String,
    'type': fields.String,
    'name': fields.String,
    'furColor': fields.String,
    'rightEyeColor': fields.String,
    'leftEyeColor': fields.String,
    'breed': fields.String,
    'size': fields.String,
    'lifeStage': fields.String,
    'age': fields.Integer,
    'sex': fields.String,
    'description': fields.String,
    'photos': fields.List(fields.Nested(
        {'photoId': fields.String }
    ))
}


class UserPets(Resource):

    USER_PETS_SCHEMA = {
        "uuid": { "type": "string", "required": True },
        "_ref": { "type": "string", "required": True },
        "type": { "type": "string", "required": True },
        "name": { "type": "string", "required": True },
        "furColor": { "type": "string" },
        "rightEyeColor": { "type": "string" },
        "leftEyeColor": { "type": "string" },
        "size": { "type": "string", "required": True },
        "age": { "type": "integer" },
        "lifeStage": { "type": "string" },
        "sex": { "type": "string", "required": True },
        "breed": { "type": "string" },
        "description": { "type": "string" },
        "photos": { 
            "type": "list",
        },
        "isMyPet": { "type": "boolean" }
    }

    def __init__(self):
        # Argument validator for Pet creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserPets, self).__init__()

    @marshal_with(pet_fields)
    def get(self, userId):
        """
        Retrieves all the pets belonging to a user.
        :param userId identifier of the owner of the pet.
        """
        try:
            userPetsURL = DATABASE_SERVER_URL + "/users/" + userId + "/pets"
            print("Issue GET to " + userPetsURL)
            response = requests.get(userPetsURL)
            if response:
                # print("Response was {}".format(response.json()))
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "No pets found for user with id {}".format(userId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR    

    @marshal_with(pet_fields)
    def post(self, userId):
        """
        Creates a pet associated to a user.
        :param userId identifier of the owner of the pet.
        :returns the new pet.
        """
        try:
            # Create the vector here??? or when creating a notice?            
            userPetsURL = DATABASE_SERVER_URL + "/users/" + userId + "/pets"
            print("Issue POST to " + userPetsURL)

            newPet = request.get_json()
            newPet["uuid"] = str(uuid.uuid4())
            newPet["_ref"] = str(uuid.uuid4())

            petPhotos = []
            # photos are sent as an array from the app
            for photo in newPet["photos"]:
                petPhotos.append({ "uuid": str(uuid.uuid4()), "photo": photo })

            newPet["photos"] = petPhotos
            if not self.arg_validator.validate(newPet, UserPets.USER_PETS_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Create pet failed, received invalid pet object {}: {}".format(newPet, self.arg_validator.errors), HTTPStatus.BAD_REQUEST

            response = requests.post(userPetsURL, json=newPet)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.CREATED
            return "Received no response from database server. Pet creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR   


class UserPet(Resource):

    USER_PET_SCHEMA = {
        "petData": {
            "type": "dict",
            "schema": {
                "_ref": { "type": "string", "required": True },
                "userId": { "type": "string" },
                "type": { "type": "string" },
                "name": { "type": "string" },
                "furColor": { "type": "string" },
                "size": { "type": "string" },
                "rightEyeColor": { "type": "string", "required": False },
                "leftEyeColor": { "type": "string", "required": False },
                "age": { "type": "integer", "required": False },
                "lifeStage": { "type": "string" },
                "sex": { "type": "string" },
                "breed": { "type": "string" },
                "description": { "type": "string" }
            }
        },
        "newPhotos": { 
            "type": "list",
        },
        "deletedPhotos": { 
            "type": "list",
        },
    }

    def __init__(self):
        # Argument validator for Pet update's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserPet, self).__init__()

    @marshal_with(pet_fields)
    def get(self, userId, petId):
        """
        Retrieves a specific pet from a user.
        :param userId identifier of the user who owns the pet.
        :param petId identifier of the pet that will be retrieved.
        """
        try:
            userPetByIdURL = DATABASE_SERVER_URL + "/users/" + userId + "/pets/" + petId
            print("Issue GET to " + userPetByIdURL)
            response = requests.get(userPetByIdURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "Pet with id {} not found for user {}".format(petId, userId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR        


    def put(self, userId, petId):
        """
        Updates a pet from a user.
        :param userId identifier of the owner of the pet.
        :param petId identifier of the pet that will be updated.
        :returns the updated pet.
        """
        try:
            petURL = DATABASE_SERVER_URL + "/users/" + userId + "/pets/" + petId
            print("Issue PUT to " + petURL)

            updatedPet = request.get_json()

            if not self.arg_validator.validate(updatedPet, UserPet.USER_PET_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Received invalid pet for update {}: {}".format(updatedPet, self.arg_validator.errors), HTTPStatus.BAD_REQUEST

            newPetPhotos = []
            for photo in updatedPet["newPhotos"]:
                newPetPhotos.append({ "uuid": str(uuid.uuid4()), "photo": photo })

            updatedPet["newPhotos"] = newPetPhotos

            response = requests.put(petURL, headers={'Content-Type': 'application/json'}, data=json.dumps(updatedPet))
            if response:
                response.raise_for_status()
                return "Successfully updated {} records".format(response.json()[0]), HTTPStatus.OK
            return "Received empy response from database server. Pet with id {} not updated for user {}".format(petId, userId), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR      

    def delete(self, userId, petId):
        """
        Deletes a pet from a user.
        :param userId identifier of the owner of the pet.
        :param petId identifier of the pet that will be deleted.
        """
        try:
            petURL = DATABASE_SERVER_URL + "/users/" + userId + "/pets/" + petId
            print("Issue DELETE to " + petURL)
            response = requests.delete(petURL)
            response.raise_for_status()
            return "Correctly deleted {} records".format(response.json()), HTTPStatus.OK
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

