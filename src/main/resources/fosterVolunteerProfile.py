import uuid
import requests

from http import HTTPStatus
from cerberus import Validator

from flask_restful import fields, request, Resource, marshal

from src.main.constants import DATABASE_SERVER_URL


# Fields returned by the src for FosterVolunteerProfile resource
profile_fields = {
    'profileId': fields.String(attribute='uuid'),
    '_ref': fields.String,
    'userId': fields.String,
    'petTypesToFoster': fields.List(fields.String),
    'petSizesToFoster': fields.List(fields.String),
    'additionalInformation': fields.String,
    'location': fields.String,
    'province': fields.String,
    'available': fields.Boolean,
    'averageRating': fields.Float,
    'ratingAmount': fields.Integer,
}


class FosterVolunteerProfile(Resource):

    FOSTER_VOLUNTEER_PROFILE_SCHEMA = {
        "_ref": {"type": "string", "required": True},
        "userId": {"type": "string"},
        "petTypesToFoster": {'type': 'list', 'schema': {'type': 'string'}},
        "petSizesToFoster": {'type': 'list', 'schema': {'type': 'string'}},
        "additionalInformation": {"type": "string"},
        "location": {"type": "string"},
        "province": {"type": "string"},
        "available": {"type": "boolean"},
        "averageRating": {"type": "float"},
        "ratingAmount": {"type": "integer"},
    }

    def __init__(self):
        # Argument parser for FosterVolunteerProfile creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(FosterVolunteerProfile, self).__init__()

    def get(self, profileId):
        """
        Retrieves a foster volunteer profile by id.
        :param profileId identifier of the profile that will be retrieved.
        """
        try:
            profileByIdURL = DATABASE_SERVER_URL + "/fosterVolunteerProfiles/" + profileId
            print("Issue GET to " + profileByIdURL)
            response = requests.get(profileByIdURL)
            if response:
                response.raise_for_status()
                return marshal(response.json(), profile_fields), HTTPStatus.OK
            return "No profile found for id {}".format(profileId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

    def put(self, profileId):
        """
        Updates the foster volunteer profile of a user.
        :param profileId identifier of the profile that will be updated.
        :returns the updated profile.
        """
        try:
            profileByIdURL = DATABASE_SERVER_URL + "/fosterVolunteerProfiles/" + profileId
            print("Issue PUT to " + profileByIdURL)
            updatedProfile = request.get_json()
            if not self.arg_validator.validate(updatedProfile, FosterVolunteerProfile.FOSTER_VOLUNTEER_PROFILE_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Received invalid profile for update {}: {}".format(updatedProfile, self.arg_validator.errors), HTTPStatus.BAD_REQUEST

            response = requests.put(profileByIdURL, json=updatedProfile)
            if response:
                response.raise_for_status()
                return marshal(response.json(), profile_fields), HTTPStatus.OK
            return "Received empty response from database server. Profile with id {} could not be updated.".format(profileId), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return "ERROR {}".format(e), HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self, profileId):
        """
        Deletes a profile from a user.
        :param profileId identifier of the profile that will be deleted.
        """
        try:
            profileByIdURL = DATABASE_SERVER_URL + "/fosterVolunteerProfiles/" + profileId
            print("Issue DELETE to " + profileByIdURL)
            response = requests.delete(profileByIdURL)
            if response:
                response.raise_for_status()
                return "Successfully deleted {} records".format(response.json()), HTTPStatus.OK
        except Exception as e:
            print("Failed to delete profile {}: {}".format(profileId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


class FosterVolunteerProfiles(Resource):

    FOSTER_VOLUNTEER_PROFILE_SCHEMA = {
        "uuid": {"type": "string", "required": True},
        **FosterVolunteerProfile.FOSTER_VOLUNTEER_PROFILE_SCHEMA
    }

    def __init__(self):
        # Argument parser for FosterVolunteerProfile creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(FosterVolunteerProfiles, self).__init__()

    def get(self):
        """
        Retrieves all the foster volunteers' profiles.
        """
        try:
            profilesURL = DATABASE_SERVER_URL + "/fosterVolunteerProfiles?" + request.query_string.decode("utf-8")
            print("Issue GET to " + profilesURL)
            response = requests.get(profilesURL)
            if response:
                response.raise_for_status()
                return marshal(response.json(), profile_fields), HTTPStatus.OK
            return "No profiles found.", HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

    def post(self):
        """
        Creates a foster volunteer profile for a user.
        :returns the new profile.
        """
        try:
            profilesURL = DATABASE_SERVER_URL + "/fosterVolunteerProfiles"
            print("Issue POST to " + profilesURL)

            newProfile = request.get_json()
            newProfile["uuid"] = str(uuid.uuid4())
            newProfile["_ref"] = str(uuid.uuid4())
            if not self.arg_validator.validate(newProfile, FosterVolunteerProfiles.FOSTER_VOLUNTEER_PROFILE_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Create foster volunteer profile failed, received invalid profile {}: {}".format(newProfile,
                                                                                     self.arg_validator.errors), HTTPStatus.BAD_REQUEST
            response = requests.post(profilesURL, json=newProfile)
            try:
                response.raise_for_status()
                return marshal(response.json(), profile_fields), HTTPStatus.CREATED
            except requests.exceptions.RequestException as e:
                print("ERROR {}".format(e))
                return "ERROR {}".format(e), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR
