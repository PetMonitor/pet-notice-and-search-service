import http
import uuid
from datetime import datetime, timezone
from enum import Enum, auto

from flask_restful import fields, reqparse, Resource, marshal_with

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")


class NoticeType(Enum):
    """ Defines the types of notices that can be created. """
    LOST = auto()
    FOUND = auto()
    STOLEN = auto()
    FOR_ADOPTION = auto()


# Fields returned by the src for the Notice resource
notice_fields = {
    'id': fields.String,
    '_ref': fields.String,
    'noticeType': fields.String,
    'eventLocation': fields.String,
    'description': fields.String,
    'eventTimestamp': fields.Float,
    'userId': fields.String,
    'petId': fields.String
}

# Fields returned by the src for the Notices resource
notices_fields = {
    'notices': fields.List(cls_or_instance=fields.Nested(notice_fields))
}

# Temporal dictionary to hold values until we make the requests to the database service
USER_ID1 = uuid.uuid4()
NOTICE_ID1 = uuid.uuid4()
USER_ID2 = uuid.uuid4()
NOTICE_ID2 = uuid.uuid4()
USER_ID3 = uuid.uuid4()
NOTICE_ID3 = uuid.uuid4()
notices_db = {
    str(USER_ID1): {
        str(NOTICE_ID1): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'noticeType': NoticeType.FOUND.name,
            'eventLocation': "CABA",
            'description': "insert text",
            'eventTimestamp': datetime.now(timezone.utc).timestamp(),
            'userId': USER_ID1,
            'petId': uuid.uuid4()
        }
    },
    str(USER_ID2): {
        str(NOTICE_ID2): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'noticeType': NoticeType.LOST.name,
            'eventLocation': "Rosario",
            'description': "insert text",
            'eventTimestamp': datetime.now(timezone.utc).timestamp(),
            'userId': USER_ID2,
            'petId': uuid.uuid4()
        }
    },
    str(USER_ID3): {
        str(NOTICE_ID3): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'noticeType': NoticeType.FOR_ADOPTION.name,
            'eventLocation': "Campana",
            'description': "insert text",
            'eventTimestamp': datetime.now(timezone.utc).timestamp(),
            'userId': USER_ID3,
            'petId': uuid.uuid4()
        }
    }
}

class Notices(Resource):

    @marshal_with(notices_fields)
    def get(self):
        """ Retrieves all the notices. """
        # TODO: Request to db server
        return {
            "notices": [list(user_notices.values()) for user_notices in notices_db.values()]
        }, http.HTTPStatus.OK


class UserNotices(Resource):

    def __init__(self):
        # Argument parser for Notice creation's JSON body
        self.create_args = _create_notice_request_parser()
        super(UserNotices, self).__init__()

    @marshal_with(notices_fields)
    def get(self, userId):
        """
        Retrieves all the notices created by a user.
        :param user_id identifier of the user who owns the notices.
        """
        # TODO: Request to db server
        if user_id in notices_db:
            return { "notices": list(notices_db[user_id].values()) }, http.HTTPStatus.OK
        return '', http.HTTPStatus.NOT_FOUND

    @marshal_with(notice_fields)
    def post(self, userId):
        """
        Creates a notice from a user.
        :param user_id identifier of the user who creates the notice.
        :returns the new notice.
        """
        args = self.create_args.parse_args()
        # TODO: Request to db server => pet should be already created (need to check first)
        new_notice = {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'noticeType': args['noticeType'],
            'eventLocation': args['eventLocation'],
            'description': args['description'],
            'eventTimestamp': args['eventTimestamp'],
            'userId': user_id,
            'petId': args['petId']
        }
        if user_id in notices_db:
            notices_db[user_id][str(new_notice['id'])] = new_notice
        else:
            notices_db[user_id] = {}
            notices_db[user_id][str(new_notice['id'])] = new_notice
        return new_notice, http.HTTPStatus.CREATED


class UserNotice(Resource):

    def __init__(self):
        # Argument parser for Notice update's JSON body
        self.update_args = _create_notice_request_parser()
        self.update_args.add_argument("_ref", type=str, help="_ref hash is required", required=True)
        super(UserNotice, self).__init__()

    @marshal_with(notice_fields)
    def get(self, userId, noticeId):
        """
        Retrieves a notice created by a user.
        :param user_id identifier of the user who owns the notice.
        :param notice_id identifier of the notice that will be retrieved.
        """
        # TODO: Request to db server
        notice = _get_user_notice(user_id, notice_id)
        if notice:
            return notice, http.HTTPStatus.OK
        return '', http.HTTPStatus.NOT_FOUND

    @marshal_with(notice_fields)
    def put(self, userId, noticeId):
        """
        Updates a notice from a user.
        :param user_id identifier of the user who owns the notice.
        :param notice_id identifier of the notice that will be updated.
        :returns the updated notice.
        """
        args = self.update_args.parse_args()
        # TODO: Request to db server
        notice = _get_user_notice(user_id, notice_id)
        if not notice:
            return '', http.HTTPStatus.NOT_FOUND
        else:
            if str(args['_ref']) == str(notice['_ref']):
                notices_db[user_id][notice_id] = {
                    'id': notice['id'],
                    '_ref': uuid.uuid4(),
                    'noticeType': args['noticeType'],
                    'eventLocation': args['eventLocation'],
                    'description': args['description'],
                    'eventTimestamp': args['eventTimestamp'],
                    'userId': notice['userId'],
                    'petId': args['petId']
                }
                return notices_db[user_id][notice_id], http.HTTPStatus.OK
            else:
                return '', http.HTTPStatus.CONFLICT

    def delete(self, userId, noticeId):
        """
        Deletes a notice from a user.
        :param user_id identifier of the user who owns the notice.
        :param notice_id identifier of the notice that will be deleted.
        """
        # TODO: Request to db server
        notice = _get_user_notice(user_id, notice_id)
        if not notice:
            return '', http.HTTPStatus.NOT_FOUND
        del notices_db[user_id][notice_id]
        if len(notices_db[user_id]) == 0:
            del notices_db[user_id]
        return '', http.HTTPStatus.NO_CONTENT

def _get_user_notice(user_id, notice_id):
    if user_id in notices_db and notice_id in notices_db[user_id]:
        return notices_db[user_id][notice_id]
    return None

def _create_notice_request_parser():
    notice_request_parser = reqparse.RequestParser()
    notice_request_parser.add_argument("noticeType", type=str, help="The type of notice is required", required=True)
    notice_request_parser.add_argument("eventLocation", type=str, help="The location of the reported event is required", required=True)
    notice_request_parser.add_argument("description", type=str, default='')
    notice_request_parser.add_argument("eventTimestamp", type=float, help="The date and hour in which the reported event occurred is required", required=True)
    notice_request_parser.add_argument("petId", type=str, help="The reported pet is required", required=True)
    return notice_request_parser
