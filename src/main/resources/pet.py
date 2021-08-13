import uuid
import requests

from os import getenv
from enum import Enum, auto
from http import HTTPStatus
from flask_restful import fields, reqparse, Resource, marshal_with
from src.main.resources.notice import USER_ID1, USER_ID2, USER_ID3

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
    'id': fields.String,
    '_ref': fields.String,
    'type': fields.String,
    'name': fields.String,
    'furColor': fields.List(cls_or_instance=fields.String),
    'eyesColor': fields.List(cls_or_instance=fields.String),
    'size': fields.String,
    'lifeStage': fields.String,
    'age': fields.Integer,
    'sex': fields.String,
    'breed': fields.String,
    'description': fields.String,
    'photos': fields.List(cls_or_instance=fields.String),
    'userId': fields.String
}

# Fields returned by the src for the Pets resource
pets_fields = {
    'pets': fields.List(cls_or_instance=fields.Nested(pet_fields))
}

# Temporal dictionary to hold values until we make the requests to the database service
PET_ID1 = uuid.uuid4()
PET_ID2 = uuid.uuid4()
PET_ID3 = uuid.uuid4()
pets_db = {
    str(USER_ID1): {
        str(PET_ID1): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'type': PetType.DOG.name,
            'name': "firulais",
            'furColor': ['brown'],
            'eyesColor': ['black'],
            'size': PetSize.SMALL.name,
            'lifeStage': PetLifeStage.ADULT.name,
            'age': 8,
            'sex': PetSex.MALE.name,
            'breed': 'crossbreed',
            'description': 'some description',
            'photos': ['test'],
            'userId': USER_ID1
        }
    },
    str(USER_ID2): {
        str(PET_ID2): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'type': PetType.DOG.name,
            'name': "blondie",
            'furColor': ['blonde'],
            'eyesColor': ['blue', 'gray'],
            'size': PetSize.MEDIUM.name,
            'lifeStage': PetLifeStage.BABY.name,
            'age': None,
            'sex': PetSex.FEMALE.name,
            'breed': 'crossbreed',
            'description': 'some description',
            'photos': ['test'],
            'userId': USER_ID2
        }
    },
    str(USER_ID3): {
        str(PET_ID3): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'type': PetType.CAT.name,
            'name': "yuli",
            'furColor': ['white', 'orange'],
            'eyesColor': ['brown'],
            'size': PetSize.SMALL.name,
            'lifeStage': PetLifeStage.ADULT.name,
            'age': 6,
            'sex': PetSex.FEMALE.name,
            'breed': 'crossbreed',
            'description': 'some description',
            'photos': ['test'],
            'userId': USER_ID3
        }
    }
}

class UserPets(Resource):

    def __init__(self):
        # Argument parser for Pet creation's JSON body
        self.create_args = _create_pet_request_parser()
        super(UserPets, self).__init__()

    @marshal_with(pets_fields)
    def get(self, userId):
        """
        Retrieves all the pets belonging to a user.
        :param user_id identifier of the owner of the pet.
        """
        try:
            userPetsURL = DATABASE_SERVER_URL + "/users/" + userId + "/pets"
            print("Issue GET to " + userPetsURL)
            response = requests.get(userPetsURL)
            if response:
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
        :param user_id identifier of the owner of the pet.
        :returns the new pet.
        """
        args = self.create_args.parse_args()
        # TODO: Request to db server
        # Create the vector here??? or when creating a notice?
        new_pet = {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
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
            'photos': args['photos'] ,
            'userId': user_id
        }
        if user_id in pets_db:
            pets_db[user_id][str(new_pet['id'])] = new_pet
        else:
            pets_db[user_id] = {}
            pets_db[user_id][str(new_pet['id'])] = new_pet
        return new_pet, HTTPStatus.CREATED


class UserPet(Resource):

    def __init__(self):
        # Argument parser for Pet update's JSON body
        self.update_args = _create_pet_request_parser()
        self.update_args.add_argument("_ref", type=str, help="_ref hash is required", required=True)
        super(UserPet, self).__init__()

    @marshal_with(pet_fields)
    def get(self, userId, petId):
        """
        Retrieves a specific pet from a user.
        :param user_id identifier of the user who owns the pet.
        :param pet_id identifier of the pet that will be retrieved.
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


    @marshal_with(pet_fields)
    def put(self, userId, petId):
        """
        Updates a pet from a user.
        :param user_id identifier of the owner of the pet.
        :param pet_id identifier of the pet that will be updated.
        :returns the updated pet.
        """
        args = self.update_args.parse_args()
        # TODO: Request to db server
        pet = _get_user_pet(user_id, pet_id)
        if not pet:
            return '', HTTPStatus.NOT_FOUND
        else:
            if str(args['_ref']) == str(pet['_ref']):
                pets_db[user_id][pet_id] = {
                    'id': pet['id'],
                    '_ref': uuid.uuid4(),
                    'type': args['type'],
                    'name': args['name'],
                    'furColor': args['furColor'],
                    'eyesColor': args['eyesColor'],
                    'size': args['size'],
                    'lifeStage': args['lifeStage'],
                    'age': args['age'],
                    'sex': args['sex'] ,
                    'breed': args['breed'] ,
                    'description': args['description'] ,
                    'photos': args['photos'] ,
                    'userId': pet['userId']
                }
                return pets_db[user_id][pet_id], HTTPStatus.OK
            else:
                return '', HTTPStatus.CONFLICT

    def delete(self, userId, petId):
        """
        Deletes a pet from a user.
        :param user_id identifier of the owner of the pet.
        :param pet_id identifier of the pet that will be deleted.
        """
        # TODO: Request to db server
        pet = _get_user_pet(user_id, pet_id)
        if not pet:
            return '', HTTPStatus.NOT_FOUND
        del pets_db[user_id][pet_id]
        if len(pets_db[user_id]) == 0:
            del pets_db[user_id]
        return '', HTTPStatus.NO_CONTENT

class SimilarPets(Resource):

    @marshal_with(pets_fields)
    def post(self):
        """
        Retrieves the pets which are near in terms of similarity to the one provided.
        """
        # TODO: Request to server
        return {
            "pets": [list(user_pets.values()) for user_pets in pets_db.values()]
        }, HTTPStatus.OK


def _get_user_pet(user_id, pet_id):
    if user_id in pets_db and pet_id in pets_db[user_id]:
        return pets_db[user_id][pet_id]
    return None


def _create_pet_request_parser():
    pet_request_parser = reqparse.RequestParser()
    pet_request_parser.add_argument("type", type=str, help="The type of pet is required", required=True)
    pet_request_parser.add_argument("name", type=str, help="The name of the pet is required", required=True)
    pet_request_parser.add_argument("furColor", type=str, action='append', help="The fur color field is required", required=True)
    pet_request_parser.add_argument("eyesColor", type=str, action='append', help="The eyes color field is required", required=True)
    pet_request_parser.add_argument("size", type=str, help="The size of the pet is required", required=True)
    pet_request_parser.add_argument("lifeStage", type=str, help="The life stage of the pet is required", required=True)
    pet_request_parser.add_argument("age", type=int)
    pet_request_parser.add_argument("sex", type=str, help="The sex of the pet is required", required=True)
    pet_request_parser.add_argument("breed", type=str, help="The breed of the pet is required", required=True)
    pet_request_parser.add_argument("description", type=str, default='')
    pet_request_parser.add_argument("photos", type=str, action='append', help="The images of the pet are required", required=True)
    pet_request_parser.add_argument("userId", type=str, help="The owner of the pet is required", required=True)
    return pet_request_parser
