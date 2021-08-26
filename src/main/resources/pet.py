import uuid
import requests

from os import getenv
from enum import Enum, auto
from http import HTTPStatus
from flask_restful import fields, reqparse, Resource, marshal_with

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")

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
    'photos': fields.List(cls_or_instance=fields.String),
}

class UserPets(Resource):

    def __init__(self):
        # Argument parser for Pet creation's JSON body
        self.create_args = _create_pet_request_parser()
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
                print("Response was {}".format(response.json()))
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
            args = self.create_args.parse_args()
            # Create the vector here??? or when creating a notice?
            newPet = {
                'uuid': uuid.uuid4(),
                'userId': userId,
                'type': args['type'],
                'name': args['name'],
                'furColor': args['furColor'],
                'rightEyeColor': args['rightEyeColor'],
                'leftEyeColor': args['leftEyeColor'],
                'size': args['size'],
                'lifeStage': args['lifeStage'],
                'age': args['age'],
                'sex': args['sex'] ,
                'breed': args['breed'] ,
                'description': args['description'] ,
                'photos': args['photos']
            }
            userPetsURL = DATABASE_SERVER_URL + "/users/" + userId + "/pets"
            print("Issue POST to " + userPetsURL)
            response = requests.post(userPetsURL, data=newPet)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.CREATED
            return "Received no response from database server. Pet creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR   

class UserPet(Resource):

    def __init__(self):
        # Argument parser for Pet update's JSON body
        self.update_args = _create_pet_request_parser()
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
            args = self.update_args.parse_args()
            # TODO: modify this to first get the pet and then
            # update only provided fields
            updatedPet = {
                    'uuid': petId,
                    'userId': args['userId'],
                    'type': args['type'],
                    'name': args['name'],
                    'furColor': args['furColor'],
                    'rightEyeColor': args['rightEyeColor'],
                    'leftEyeColor': args['leftEyeColor'],
                    'size': args['size'],
                    'lifeStage': args['lifeStage'],
                    'age': args['age'],
                    'sex': args['sex'],
                    'breed': args['breed'],
                    'description': args['description'],
                    'photos': args['photos']
                }

            response = requests.put(petURL, data=updatedPet)
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
            if response:
                response.raise_for_status()
                return "Correctly deleted {} records".format(response.json()), HTTPStatus.OK
            return "Received empy response from database server. Pet with id {} not updated for user {}".format(petId, userId), HTTPStatus.INTERNAL_SERVER_ERROR            
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR      


"""
Similar pet search resource.
"""
class SimilarPets(Resource):

    @marshal_with(pet_fields)
    def post(self):
        """
        Retrieves the pets which are near in terms of similarity to the one provided.
        """
        # TODO: Request to server
        return {
            "pets": []
        }, HTTPStatus.OK


def _create_pet_request_parser():
    pet_request_parser = reqparse.RequestParser()
    pet_request_parser.add_argument("type", type=str, help="The type of pet is required", required=False)
    pet_request_parser.add_argument("name", type=str, help="The name of the pet is required", required=False)
    pet_request_parser.add_argument("furColor", type=str, help="The fur color field is required", required=False)
    pet_request_parser.add_argument("rightEyeColor", type=str, help="The eyes color field is required", required=False)
    pet_request_parser.add_argument("leftEyeColor", type=str, help="The eyes color field is required", required=False)
    pet_request_parser.add_argument("size", type=str, help="The size of the pet is required", required=False)
    pet_request_parser.add_argument("lifeStage", type=str, help="The life stage of the pet is required", required=False)
    pet_request_parser.add_argument("age", type=int, required=False)
    pet_request_parser.add_argument("sex", type=str, help="The sex of the pet is required", required=False)
    pet_request_parser.add_argument("breed", type=str, help="The breed of the pet is required", required=False)
    pet_request_parser.add_argument("description", type=str, default='')
    pet_request_parser.add_argument("photos", type=str, help="The images of the pet are required", required=False) 
    pet_request_parser.add_argument("userId", type=str, help="The owner of the pet is required", required=False)
    return pet_request_parser
