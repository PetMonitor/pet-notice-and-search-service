import requests
import io
from os import getenv
from http import HTTPStatus
from cerberus import Validator
from flask_restful import Resource
from flask import send_file

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")


class Photo(Resource):

    def __init__(self):
        # Argument validator for Pet creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(Photo, self).__init__()

    def get(self, photoId):
        """
        Retrieves all the pets belonging to a user.
        :param userId identifier of the owner of the pet.
        """
        try:
            photoURL = DATABASE_SERVER_URL + "/photos/" + photoId
            print("Issue GET to " + photoURL)
            response = requests.get(photoURL)
            if response:
                print("Response was {}".format(response.raw))
                response.raise_for_status()
                return send_file(io.BytesIO(response.content), 'image/png')
            return "No photos found for with id {}".format(photoId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR
