import http
import uuid
from enum import Enum, auto

from flask_restful import fields, reqparse, Resource, marshal_with

from src.resources.notice import USER_ID1, USER_ID2, USER_ID3


class PetType(Enum):
    DOG = auto()
    CAT = auto()

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
            'type': PetType.DOG,
            'name': "firulais",
            'furColor': ['brown'],
            'eyesColor': ['black'],
            'size': 'small',
            'lifeStage': 'adult',
            'age': 8,
            'sex': 'male',
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
            'type': PetType.DOG,
            'name': "blondie",
            'furColor': ['blonde'],
            'eyesColor': ['blue', 'gray'],
            'size': 'medium',
            'lifeStage': 'puppy',
            'age': None,
            'sex': 'female',
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
            'type': PetType.CAT,
            'name': "yuli",
            'furColor': ['white', 'orange'],
            'eyesColor': ['brown'],
            'size': 'small',
            'lifeStage': 'adult',
            'age': 6,
            'sex': 'female',
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
    def get(self, user_id):
        """
        Retrieves all the pets belonging to a user.
        :param user_id identifier of the owner of the pet.
        """
        # TODO: Request to db server
        if user_id in pets_db:
            return {"pets": list(pets_db[user_id].values())}, http.HTTPStatus.OK
        return '', http.HTTPStatus.NOT_FOUND

    @marshal_with(pet_fields)
    def post(self, user_id):
        """
        Creates a pet from a user.
        :param user_id identifier of the owner of the pet.
        :returns the new pet.
        """
        args = self.create_args.parse_args()
        # TODO: Request to db server
        new_pet = {
            'id': uuid.uuid4(),
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
            'userId': user_id
        }
        if user_id in pets_db:
            pets_db[user_id][str(new_pet['id'])] = new_pet
        else:
            pets_db[user_id] = {}
            pets_db[user_id][str(new_pet['id'])] = new_pet
        return new_pet, http.HTTPStatus.CREATED


class UserPet(Resource):

    def __init__(self):
        # Argument parser for Pet update's JSON body
        self.update_args = _create_pet_request_parser()
        self.update_args.add_argument("_ref", type=str, help="_ref hash is required", required=True)
        super(UserPet, self).__init__()

    @marshal_with(pet_fields)
    def get(self, user_id, pet_id):
        """
        Retrieves a specific pet from a user.
        :param user_id identifier of the user who owns the pet.
        :param pet_id identifier of the pet that will be retrieved.
        """
        # TODO: Request to db server
        pet = _get_user_pet(user_id, pet_id)
        if pet:
            return pet, http.HTTPStatus.OK
        return '', http.HTTPStatus.NOT_FOUND

    @marshal_with(pet_fields)
    def put(self, user_id, pet_id):
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
            return '', http.HTTPStatus.NOT_FOUND
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
                return pets_db[user_id][pet_id], http.HTTPStatus.OK
            else:
                return '', http.HTTPStatus.CONFLICT

    def delete(self, user_id, pet_id):
        """
        Deletes a pet from a user.
        :param user_id identifier of the owner of the pet.
        :param pet_id identifier of the pet that will be deleted.
        """
        # TODO: Request to db server
        pet = _get_user_pet(user_id, pet_id)
        if not pet:
            return '', http.HTTPStatus.NOT_FOUND
        del pets_db[user_id][pet_id]
        if len(pets_db[user_id]) == 0:
            del pets_db[user_id]
        return '', http.HTTPStatus.NO_CONTENT

class SimilarPets(Resource):

    @marshal_with(pets_fields)
    def post(self):
        """
        Retrieves the pets which are near in terms of similarity to the one provided.
        """
        # TODO: Request to server
        return {
            "pets": [list(user_pets.values()) for user_pets in pets_db.values()]
        }, http.HTTPStatus.OK


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
