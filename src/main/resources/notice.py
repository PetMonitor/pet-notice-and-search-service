import uuid
import requests

from os import getenv
from http import HTTPStatus
from enum import Enum, auto
from cerberus import Validator

from flask_restful import fields, request, Resource, marshal_with

from src.main.constants import DATABASE_SERVER_URL


class NoticeType(Enum):
    """ Defines the types of notices that can be created. """
    LOST = auto()
    FOUND = auto()
    STOLEN = auto()
    FOR_ADOPTION = auto()


# Fields returned by the src for Notice resource
notice_fields = {
    'noticeId': fields.String(attribute='uuid'),
    '_ref': fields.String,
    'noticeType': fields.String,
    'description': fields.String,
    'eventTimestamp': fields.String,
    'userId': fields.String,
    'pet': {
        'id': fields.String(attribute='petId'),
        'photo': fields.List(fields.Integer, attribute='petPhoto.data')
    },
    'eventLocation': {
        'lat': fields.Float(attribute='eventLocationLat'),
        'long': fields.Float(attribute='eventLocationLong')
    },
    'street': fields.String,
    'neighbourhood': fields.String,
    'locality': fields.String,
    'country': fields.String,
}


class Notices(Resource):

    @marshal_with(notice_fields)
    def get(self):
        """ 
        Retrieves all the notices. 
        """
        try:
            noticesURL = DATABASE_SERVER_URL + "/notices?" + request.query_string.decode("utf-8")
            print("Issue GET to " + noticesURL)
            response = requests.get(noticesURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "No notices found.", HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  

    @marshal_with(notice_fields)
    def get(self, noticeId):
        """
        Retrieves a notice by id.
        :param noticeId identifier of the notice that will be retrieved.
        """
        try:
            noticeByIdURL = DATABASE_SERVER_URL + "/notices/" + noticeId
            print("Issue GET to " + noticeByIdURL)
            response = requests.get(noticeByIdURL)
            if response:
                response.raise_for_status()

            return response.json(), HTTPStatus.OK
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR 

class UserNotices(Resource):

    USER_NOTICES_SCHEMA = {
        "uuid": { "type": "string", "required": True },
        "_ref": { "type": "string", "required": True },
        "petId": { "type": "string" },
        "noticeType": { "type": "string" },
        "eventLocation": { 
            "type": "dict", 
            "require_all": True,
            "schema": {
                "lat": { "type": "float" },
                "long": { "type": "float" }
            }
        },
        "street": { "type": "string" },
        "neighbourhood": { "type": "string" },
        "locality": { "type": "string" },
        "country": { "type": "string" },
        "description": { "type": "string" },
        "eventTimestamp": { "type": "string" }
    }

    def __init__(self):
        # Argument parser for Notice creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserNotices, self).__init__()

    @marshal_with(notice_fields)
    def get(self, userId):
        """
        Retrieves all the notices created by a user.
        :param userId identifier of the user who owns the notices.
        """
        try:
            userNoticesURL = DATABASE_SERVER_URL + "/users/" + userId + "/notices"
            print("Issue GET to " + userNoticesURL)
            response = requests.get(userNoticesURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "No notices found for user with id {}".format(userId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR    

    @marshal_with(notice_fields)
    def post(self, userId):
        """
        Creates a notice from a user.
        :param userId identifier of the user who creates the notice.
        :returns the new notice.
        """
        try:
            userNoticesURL = DATABASE_SERVER_URL + "/users/" + userId + "/notices"
            print("Issue POST to " + userNoticesURL)

            newNotice = request.get_json()
            newNotice["uuid"] = str(uuid.uuid4())
            newNotice["_ref"] = str(uuid.uuid4())
            if not self.arg_validator.validate(newNotice, UserNotices.USER_NOTICES_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Create notice failed, received invalid notice {}: {}".format(newNotice, self.arg_validator.errors), HTTPStatus.BAD_REQUEST
            
            if "eventLocation" in newNotice:
                newNotice["eventLocationLat"] = newNotice["eventLocation"]["lat"]
                newNotice["eventLocationLong"] = newNotice["eventLocation"]["long"]
                del newNotice["eventLocation"]
            response = requests.post(userNoticesURL, data=newNotice)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.CREATED
            return "Received no response from database server. Notice creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR   


class UserNotice(Resource):

    USER_NOTICE_SCHEMA = {
        "_ref": { "type": "string", "required": True },
        "petId": { "type": "string", "required": False },
        "noticeType": { "type": "string", "required": False },
        "eventLocation": { 
            "type": "dict", 
            "require_all": True,
            "schema":{
                "lat": { "type": "float" },
                "long": { "type": "float" }
            },
            "required": False 
        },
        "street": { "type": "string", "required": False },
        "neighbourhood": { "type": "string", "required": False },
        "locality": { "type": "string", "required": False },
        "country": { "type": "string", "required": False },
        "description": { "type": "string", "required": False },
        "eventTimestamp": { "type": "string", "required": False }
    }

    def __init__(self):
        # Argument validator for Notice update's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(UserNotice, self).__init__()

    @marshal_with(notice_fields)
    def get(self, userId, noticeId):
        """
        Retrieves a notice created by a user.
        :param userId identifier of the user who owns the notice.
        :param noticeId identifier of the notice that will be retrieved.
        """
        try:
            userNoticeByIdURL = DATABASE_SERVER_URL + "/users/" + userId + "/notices/" + noticeId
            print("Issue GET to " + userNoticeByIdURL)
            response = requests.get(userNoticeByIdURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "No notice with id {} found for user with id {}".format(noticeId, userId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR   

    def put(self, userId, noticeId):
        """
        Updates a notice from a user.
        :param userId identifier of the user who owns the notice.
        :param noticeId identifier of the notice that will be updated.
        :returns the updated notice.
        """
        try:
            userNoticeByIdURL = DATABASE_SERVER_URL + "/users/" + userId + "/notices/" + noticeId
            print("Issue PUT to " + userNoticeByIdURL)
            updatedNotice = request.get_json()
            if not self.arg_validator.validate(updatedNotice, UserNotice.USER_NOTICE_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Received invalid notice for update {}: {}".format(updatedNotice, self.arg_validator.errors), HTTPStatus.BAD_REQUEST
            
            if "eventLocation" in updatedNotice:
                updatedNotice["eventLocationLat"] = updatedNotice["eventLocation"]["lat"]
                updatedNotice["eventLocationLong"] = updatedNotice["eventLocation"]["long"]
                del updatedNotice["eventLocation"]
            response = requests.put(userNoticeByIdURL, data=updatedNotice)
            if response:
                response.raise_for_status()
                return "Successfully updated {} records".format(response.json()[0]), HTTPStatus.OK
            return "Received empty response from database server. Notice with id {} for user {} could not be updated.".format(noticeId, userId), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return "ERROR {}".format(e), HTTPStatus.INTERNAL_SERVER_ERROR    


    def delete(self, userId, noticeId):
        """
        Deletes a notice from a user.
        :param user_id identifier of the user who owns the notice.
        :param notice_id identifier of the notice that will be deleted.
        """
        try:
            userNoticeByIdURL = DATABASE_SERVER_URL + "/users/" + userId + "/notices/" + noticeId
            print("Issue DELETE to " + userNoticeByIdURL)
            response = requests.delete(userNoticeByIdURL)
            if response:
                response.raise_for_status()
                return "Successfully deleted {} records".format(response.json()), HTTPStatus.OK
        except Exception as e:
            print("Failed to delete user {}: {}".format(userId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR
