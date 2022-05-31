import io
import re
import requests
from os import getenv
from http import HTTPStatus
from cerberus import Validator
from flask_restful import Resource
from flask import send_file

from src.main.constants import DATABASE_SERVER_URL


class Photo(Resource):

    def __init__(self):
        # Argument validator for Pet creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(Photo, self).__init__()

    def get(self, photoId):
        """
        Retrieves all photos with specified id
        :param photoId identifier of the photo to be retrieved.
        """
        try:
            photoURL = DATABASE_SERVER_URL + "/photos/" + photoId
            print("Issue GET to " + photoURL)
            response = requests.get(photoURL)
            if response and response.status_code == HTTPStatus.OK:
                print("Response was {}".format(response.raw))
                return send_file(io.BytesIO(response.content), 'image/png')
            resp = { "reason":"No photos found for with id {}".format(photoId) }    
            return  resp.json(), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


class UserProfilePicture(Resource):

    def __init__(self):
        # Argument validator for Pet creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserProfilePicture, self).__init__()

    def get(self, userId):
        """
        Retrieves a user's profile picture.
        :param userId identifier.
        """
        try:
            photoURL = DATABASE_SERVER_URL + "/photos/profile/" + userId
            print("Issue GET to " + photoURL)
            response = requests.get(photoURL)
            
            if response.status_code != HTTPStatus.OK:
                print("GET to " + photoURL + " returned status code " + str(response.status_code))
                return "", response.status_code

            print("Response was {}".format(response.raw))
            return send_file(io.BytesIO(response.content), 'image/png')
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR