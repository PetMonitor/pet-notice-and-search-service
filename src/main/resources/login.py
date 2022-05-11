import requests

from os import getenv
from http import HTTPStatus
from cerberus import Validator
from src.main.utils.jwtGenerator import JwtGenerator
from src.main.utils.requestAuthorizer import RequestAuthorizer

from flask_restful import fields, request, Resource, marshal_with
from flask import session

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://192.168.64.2:4000")

# Fields returned by the src for the UserLogin resource
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
            
            # Validate user credentials
            response = requests.post(DATABASE_SERVER_URL + "/users/credentialValidation", data=userCredentials)
            print("Received response {}".format(response))

            if not response:
                return "Received empty response from database server. User creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR

            #TODO: no se por que, esta validacion se la pasa y direcamente
            #hace el raise status
            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                return "Invalid credentials: invalid username or password provided", HTTPStatus.UNAUTHORIZED
            
            response.raise_for_status() 
            user = response.json()
            
            user["sessionToken"] = JwtGenerator.generateToken(user)
            session[user["sessionToken"]] = user
            return user, HTTPStatus.OK
        except Exception as e:
            print("User login failed: {}".format(str(e)))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


class UserLogout(Resource):

    def __init__(self):
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserLogout, self).__init__()

    def post(self):
        """
        Logout endpoint for users.
        """
        try:
            print("User logout")
            if not RequestAuthorizer.isRequestAuthorized(request):
                return "Request unauthorized: user session not found", HTTPStatus.UNAUTHORIZED
            authBearer = request.headers.get('Authorization')
            (_, sessionToken) = authBearer.split(' ')
            session.pop(sessionToken)
            return "Logout success", HTTPStatus.OK
        except Exception as e:
            print("User logout failed: {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR