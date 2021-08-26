import uuid
import requests

from os import getenv
from http import HTTPStatus
from enum import Enum, auto

from flask_restful import fields, reqparse, Resource, marshal_with

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")

class NoticeType(Enum):
    """ Defines the types of notices that can be created. """
    LOST = auto()
    FOUND = auto()
    STOLEN = auto()
    FOR_ADOPTION = auto()

notice_fields = {
    'noticeId': fields.String(attribute='uuid'),
    'noticeType': fields.String,
    'description': fields.String,
    'eventTimestamp': fields.String,
    'userId': fields.String,
    'petId': fields.String
}
notice_fields['eventLocation'] = {}
notice_fields['eventLocation']['lat'] = fields.String(attribute='eventLocationLat')
notice_fields['eventLocation']['long'] = fields.String(attribute='eventLocationLong')

class Notices(Resource):

    @marshal_with(notice_fields)
    def get(self):
        """ 
        Retrieves all the notices. 
        """
        try:
            noticesURL = DATABASE_SERVER_URL + "/notices"
            print("Issue GET to " + noticesURL)
            response = requests.get(noticesURL)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.OK
            return "No notices found.", HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  


class UserNotices(Resource):

    def __init__(self):
        # Argument parser for Notice creation's JSON body
        self.create_args = _create_notice_request_parser()
        super(UserNotices, self).__init__()

    @marshal_with(notice_fields)
    def get(self, userId):
        """
        Retrieves all the notices created by a user.
        :param user_id identifier of the user who owns the notices.
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
        :param user_id identifier of the user who creates the notice.
        :returns the new notice.
        """
        try:
            args = self.create_args.parse_args()
            newNotice = {
              'uuid': uuid.uuid4(),
              'noticeType': args['noticeType'],
              'eventLocation': args['eventLocation'],
              'description': args['description'],
              'eventTimestamp': args['eventTimestamp'],
              'userId': userId,
              'petId': args['petId']
            }
            userNoticesURL = DATABASE_SERVER_URL + "/users/" + userId + "/notices"
            print("Issue POST to " + userNoticesURL)
            response = requests.post(userNoticesURL, data=newNotice)
            if response:
                response.raise_for_status()
                return response.json(), HTTPStatus.CREATED
            return "Received no response from database server. Notice creation failed.", HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR   


class UserNotice(Resource):

    def __init__(self):
        # Argument parser for Notice update's JSON body
        self.update_args = _create_notice_request_parser()
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
            args = self.update_args.parse_args()
            updatedNotice = {
                'noticeType': args['noticeType'],
                'eventLocation': args['eventLocation'],
                'description': args['description'],
                'eventTimestamp': args['eventTimestamp'],
                'userId': userId,
                'petId': args['petId']
            }

            response = requests.put(userNoticeByIdURL, data=updatedNotice)
            if response:
                response.raise_for_status()
                return "Successfully updated {} records".format(response.json()[0]), HTTPStatus.OK
            return "Received empy response from database server. Notice with id {} for user {} could not be updated.".format(noticeId, userId), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR    


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

def _create_notice_request_parser():
    notice_request_parser = reqparse.RequestParser()
    notice_request_parser.add_argument("noticeType", type=str, help="The type of notice is required", required=False)
    notice_request_parser.add_argument("eventLocation", type=list, help="The location (latitude and longitude coordinates) of the reported event is required", required=False)
    notice_request_parser.add_argument("description", type=str, default='')
    notice_request_parser.add_argument("eventTimestamp", type=str, help="The date and hour in which the reported event occurred is required", required=False)
    notice_request_parser.add_argument("petId", type=str, help="The reported pet is required", required=False)
    return notice_request_parser
