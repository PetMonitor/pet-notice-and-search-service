import uuid
import requests
import json
from os import getenv
from http import HTTPStatus
from cerberus import Validator

from flask_restful import fields, request, Resource, marshal_with

from src.main.utils.requestAuthorizer import RequestAuthorizer

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")

# Fields returned by the src for the User resource
user_fields = {
    "userId": fields.String(attribute="uuid"),
    "_ref": fields.String,
    "username": fields.String,
    "email": fields.String,
    "name": fields.String,
    "phoneNumber": fields.String,
    "alertsActivated": fields.Boolean,
    "alertRadius": fields.Integer,
    "profilePicture": fields.String
}


class User(Resource):

    USER_SCHEMA = {
        "_ref": { "type": "string", "required": True },
        "username": { "type": "string", "required": False },
        "password": { "type": "string", "required": False },
        "email": { "type": "string", "required": False },
        "name": { "type": "string", "required": False, "nullable": True },
        "phoneNumber": { "type": "string", "required": False, "nullable": True },
        "alertsActivated": { "type": "boolean", "required": False },
        "alertRadius": { "type": "integer", "required": False },
        "profilePicture": { "type": "string", "required": False, "nullable": True }
    }

    def __init__(self):
        # Argument validator for User methods' JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(User, self).__init__()

    @marshal_with(user_fields)
    def get(self, userId):
        """
        Retrieves a specific user's profile information.
        :param userId identifier of the user.
        """
        try:
            if not RequestAuthorizer.authenticateRequester(userId, request):
                return "Request unauthorized: user session not found", HTTPStatus.UNAUTHORIZED
            usersByIdURL = DATABASE_SERVER_URL + "/users/" + userId
            print("Issue GET to " + usersByIdURL)
            response = requests.get(usersByIdURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "User with id {} not found".format(userId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("Failed to get user {}: {}".format(userId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR
    
    def put(self, userId):
        """
        Modifies the user with the provided user id.
        :param userId identifier of the user.
        """
        try:
            if not RequestAuthorizer.authenticateRequester(userId, request):
                return "Request unauthorized: user session not found", HTTPStatus.UNAUTHORIZED
            updateUserURL = DATABASE_SERVER_URL + "/users/" + userId
            print("Issue PUT to " + updateUserURL)

            updatedUser = request.get_json()
            if not self.arg_validator.validate(updatedUser, User.USER_SCHEMA):
                print("VALIDATION ERROR: {}".format(self.arg_validator.errors))
                return "Received invalid user for update {}: {}".format(updatedUser, self.arg_validator.errors), HTTPStatus.BAD_REQUEST

            response = requests.put(updateUserURL, data=updatedUser)
            if response:
                response.raise_for_status()
                return "Successfully updated {} records".format(response.json()['updatedCount']), HTTPStatus.OK
        except Exception as e:
            print("Failed to update user {}: {}".format(userId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self, userId):
        """
        Deletes the user with the provided user id.
        :param userId identifier of the user.
        """
        try:
            if not RequestAuthorizer.authenticateRequester(userId, request):
                return "Request unauthorized: user session not found", HTTPStatus.UNAUTHORIZED
            deleteUserURL = DATABASE_SERVER_URL + "/users/" + userId
            print("Issue DELETE to " + deleteUserURL)
            response = requests.delete(deleteUserURL)
            if response:
                response.raise_for_status()
                return "Successfully deleted {} records".format(response.json()['deletedCount']), HTTPStatus.OK
        except Exception as e:
            print("Failed to delete user {}: {}".format(userId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


class UserPwd(Resource):

    USER_PWD_SCHEMA = {
        "_ref": { "type": "string", "required": True },
        "oldPassword": { "type": "string", "required": True },
        "newPassword": { "type": "string", "required": True }
    }

    def __init__(self):
        # Argument validator for UserPwd methods' body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserPwd, self).__init__()

    def put(self, userId):
        try:
            if not RequestAuthorizer.authenticateRequester(userId, request):
                return "Request unauthorized: user session not found", HTTPStatus.UNAUTHORIZED
            updateUserURL = DATABASE_SERVER_URL + "/users/" + userId + "/password"
            print("Issue PUT to " + updateUserURL)

            updatedUserPwd = request.get_json()
            if not self.arg_validator.validate(updatedUserPwd, UserPwd.USER_PWD_SCHEMA):
                print("VALIDATION ERROR: {}".format(self.arg_validator.errors))
                return "Received invalid user password for update".format(self.arg_validator.errors), HTTPStatus.BAD_REQUEST

            response = requests.put(updateUserURL, data=updatedUserPwd)
            if response:
                response.raise_for_status()
                return "Successfully updated {} records".format(response.json()['updatedCount']), HTTPStatus.OK
        except Exception as e:
            print("Failed to update user {}: {}".format(userId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR        


class Users(Resource):

    USERS_SCHEMA = {
        "uuid": { "type": "string", "required": True },
        "_ref": { "type": "string", "required": True },
        "username": { "type": "string", "required": True },
        "password": { "type": "string", "required": True },
        "email": { "type": "string" },
        "pets": { 
            "type": "list", 
            "required": False, 
            "schema": {   
                "type": "dict",
                "schema": { 
                    "uuid": { "type": "string", "required": True },
                    "_ref": { "type": "string", "required": True },
                    "type": { "type": "string" },
                    "name": { "type": "string" },
                    "furColor": { "type": "string" },
                    "size": { "type": "string" },
                    "lifeStage": { "type": "string" },
                    "sex": { "type": "string" },
                    "breed": { "type": "string" },
                    "description": { "type": "string" },
                    "photos": {
                        "type": "list", 
                        "required": False, 
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "uuid": { "type": "string", "required": True },
                                "photo": { "type": "string", "required": True },
                            }

                        }
                    }
                }
        }}
    }

    def __init__(self):
        # Argument validator for Pet creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(Users, self).__init__()

    @marshal_with(user_fields)
    def get(self):
        """
        Retrieves a list of all registered users.
        """
        try:
            print("Get users")
            if not RequestAuthorizer.isRequestAuthorized(request):
                return "Request unauthorized: user session not found", HTTPStatus.UNAUTHORIZED
            allUsersURL = DATABASE_SERVER_URL + "/users"
            print("Issue GET to " + allUsersURL)
            response = requests.get(allUsersURL)
            if response:
                response.raise_for_status()
                print("Response was {}".format(response.json()))
                return response.json(), HTTPStatus.OK
            return "Received empty response from server for GET /users", HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

    @marshal_with(user_fields)
    def post(self):
        """
        Creates a new user profile.
        """
        try:
            newUser = request.get_json()
            newUser["uuid"] = str(uuid.uuid4())
            newUser["_ref"] = str(uuid.uuid4())

            if "pets" in newUser:
                for pet in newUser["pets"]:
                    pet["uuid"] = str(uuid.uuid4())
                    pet["_ref"] = str(uuid.uuid4())

                    petPhotos = []
                    # photos are sent as an array from the app
                    for photo in pet["photos"]:
                        petPhotos.append({ "uuid": str(uuid.uuid4()), "photo": photo })

                    pet["photos"] = petPhotos
                
                # print('Received user with pets {}'.format(newUser))
            if not self.arg_validator.validate(newUser, Users.USERS_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Unable to create user, received invalid user {}: {}".format(newUser, self.arg_validator.errors), HTTPStatus.BAD_REQUEST

            # print('Creating user {}'.format(newUser))
            response = requests.post(DATABASE_SERVER_URL + "/users", headers={'Content-Type': 'application/json'}, data=json.dumps(newUser))
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.CREATED
            return "Received empty response from database server. User creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("Failed to create user: {}", e)
            return e, HTTPStatus.INTERNAL_SERVER_ERROR
