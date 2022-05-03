import requests
from os import getenv
from http import HTTPStatus
from cerberus import Validator

from flask_restful import fields, request, Resource, marshal_with

from src.main.utils.requestAuthorizer import RequestAuthorizer

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")

# Fields returned by the src for the User resource
user_fields = {
    "userId": fields.String(attribute="uuid")
}


class FacebookUser(Resource):

    def __init__(self):
        # Argument validator for User methods' JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(FacebookUser, self).__init__()

    @marshal_with(user_fields)
    def get(self, facebookId):
        """
        Retrieves a specific user's profile information.
        :param facebookId facebook identifier of the user.
        """
        try:
            facebookUsersByIdURL = DATABASE_SERVER_URL + "/users/facebook/" + facebookId
            print("Issue GET to " + facebookUsersByIdURL)
            response = requests.get(facebookUsersByIdURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "User with facebookId {} not found".format(facebookId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("Failed to get user {}: {}".format(facebookId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

