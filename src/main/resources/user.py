import uuid
import requests

from os import getenv
from enum import Enum, auto
from http import HTTPStatus
from flask_restful import fields, reqparse, Resource, marshal_with

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")

# Fields returned by the src for the User resource
user_fields = {
    "userId": fields.String(attribute="uuid"),
    "_ref": fields.String,
    "username": fields.String,
    "password": fields.String,
    "email": fields.String
}

class User(Resource):
    def __init__(self):
        # Argument parser for Pet creation's JSON body
        self.create_args = _create_user_request_parser()
        super(User, self).__init__()

    @marshal_with(user_fields)
    def get(self, userId):
        """
        Retrieves a specific user's profile information.
        :param userId identifier of the user.
        """
        try:
            usersByIdURL = DATABASE_SERVER_URL + "/users/" + userId
            print("Issue GET to " + usersByIdURL)
            response = requests.get(usersByIdURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "User with id {} not found".format(userId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

class Users(Resource):
    def __init__(self):
        # Argument parser for Pet creation's JSON body
        self.create_args = _create_user_request_parser()
        super(Users, self).__init__()

    @marshal_with(user_fields)
    def get(self):
        """
        Retrieves a list of all registered users.
        """
        try:
            allUsersURL = DATABASE_SERVER_URL + "/users"
            print("Issue GET to " + allUsersURL)
            response = requests.get(allUsersURL)
            if response:
                response.raise_for_status()
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
            args = self.create_args.parse_args()
            newUser = {
                "uuid": uuid.uuid4(),
                "_ref": uuid.uuid4(),
                "username": args["username"],
                "password": args["password"],
                "email": args["email"]
            }
            response = requests.post(DATABASE_SERVER_URL + "/users", data=newUser)
            if response:
                response.raise_for_status()
                return newUser["uuid"], HTTPStatus.CREATED
            return "Received empty response from database server. User creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


def _create_user_request_parser():
    user_request_parser = reqparse.RequestParser()
    user_request_parser.add_argument("username", type=str, help="A username is required", required=True)
    user_request_parser.add_argument("password", type=str, help="The name of the pet is required", required=True)
    user_request_parser.add_argument("email", type=str, required=False)
    return user_request_parser