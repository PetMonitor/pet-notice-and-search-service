import uuid
import requests

from os import getenv
from http import HTTPStatus
from cerberus import Validator

from flask_restful import fields, request, Resource, marshal_with
from flask import session

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")

# Fields returned by the src for the User resource
user_fields = {
    "userId": fields.String(attribute="uuid"),
    "_ref": fields.String,
    "username": fields.String,
    "email": fields.String,
    "sessionToken": fields.String
}

class UserLogin(Resource):

    USER_CREDENTIALS_SCHEMA = {
        "username": { "type": "string" },
        "password": { "type": "string" }
    }

    def __init__(self):
        # Argument validator for user's login JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserLogin, self).__init__()

    @marshal_with(user_fields)
    def post(self):
        """
        Login endpoint for users.
        """        
        try:
            print("User login")
            userCredentials = request.get_json()
            if not self.arg_validator.validate(userCredentials, UserLogin.USER_CREDENTIALS_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Unable to login user, received invalid login data {}: {}".format(userCredentials, self.arg_validator.errors), HTTPStatus.BAD_REQUEST
            
            print("Session {}".format(session))

            if userCredentials["username"] in session:
                print("User {} already logged in.".format(userCredentials["username"]))
                return session[userCredentials["username"]], HTTPStatus.OK    
            
            # Validate credentials
            response = requests.post(DATABASE_SERVER_URL + "/users/credentialValidation", data=userCredentials)
            print("Received response {}".format(response))

            if response == None:
                return "Received empty response from database server. User creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR

            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                return "Invalid credentials: invalid username or password provided", HTTPStatus.UNAUTHORIZED
            
            response.raise_for_status() 
            user = response.json()
            
            # TODO: generate a session token
            user["sessionToken"] = "someSessionToken"
            session[user["username"]] = user
            return user, HTTPStatus.OK
        except Exception as e:
            print("User login failed: {}".format(str(e)))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


class UserLogout(Resource):

    def __init__(self):
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserLogout, self).__init__()

    def post(self, userId):
        """
        Login endpoint for users.
        """
        # Validate request
        # Validate credentials against database service
        # Return a session token (if the transaction is in the database service maybe generate it there)
        try:
            print("User logout")
            if userId in  session:
                session.pop(userId)
                return "Logout success", HTTPStatus.OK
            return "User session unavailable", HTTPStatus.NOT_FOUND
        except Exception as e:
            print("User logout failed: {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR