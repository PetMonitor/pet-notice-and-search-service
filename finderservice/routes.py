from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with
from finderservice import app, api
from enum import Enum, auto


@app.route('/')
def hello_world():
    return 'Hello World!!'

@app.route('/reports')
def get_reports():
    return "hi"


def get_reports_from_user(user_id):
    pass


def create_report_from_user(user_id):
    pass


class ReportType(Enum):
    LOST = auto()
    FOUND = auto()
    STOLEN = auto()
    FOR_ADOPTION = auto()


class PetType(Enum):
    DOG = auto()
    CAT = auto()

report_create_args = reqparse.RequestParser()
report_create_args.add_argument("report_type", type=ReportType, help="Type of report is required", required=True)
report_create_args.add_argument("event_location", type=str, help="Location of the reported event is required", required=True)
report_create_args.add_argument("description", type=str, help="Extra information included in the report")
report_create_args.add_argument("event_timestamp", type=int, help="Date and hour in which the reported event occurred is required", required=True)
report_create_args.add_argument("pet", type=str, help="Pet reported is required", required=True)

pet_fields = {
    'type': fields.String,
    'name': fields.String,
    'furColor': fields.List(cls_or_instance=fields.String),
    'eyesColor': fields.List(cls_or_instance=fields.String),
    'size': fields.String,
    'lifeStage': fields.String,
    'age': fields.Integer,
    'sex': fields.String,
    'breed': fields.String,
    'photos': fields.List(cls_or_instance=fields.String)
}

report_fields = {
    'id': fields.String,
    '_ref': fields.String,
    'reportType': fields.String,
    'eventLocation': fields.Integer,
    'description': fields.String,
    'eventTimestamp': fields.Integer,
    'userId': fields.Integer,
    'pet': fields.Nested(nested=pet_fields)
}

class Reports(Resource):
    def get(self):
        return {"reports": 800}

class MyReports(Resource):
    def get(self, user_id):
        return {"user": user_id}

    def post(self, user_id):
        # args = report_create_args.parse_args()
        return {"user": user_id}

class Report(Resource):
    # @marshal_with(report_fields)
    def put(self, user_id, report_id):
        return {"user": user_id, "report": report_id}

    # @marshal_with(report_fields)
    def delete(self, user_id, report_id):
        # return args, 201
        return {"user": user_id, "report": report_id}

api.add_resource(Reports, '/reports')
api.add_resource(MyReports, '/users/<string:user_id>/reports')
api.add_resource(Report, '/users/<string:user_id>/reports/<string:report_id>')

@app.route('/users/<user_id>/reports', methods=['GET', 'POST'])
def my_reports(user_id):
    if request.method == 'GET':
        return get_reports_from_user(user_id)
    elif request.method == 'POST':
        return create_report_from_user(user_id)
    return error_response(405, f"Method {request.method} not allowed")


''' Returns the JSON structure for an error response. It's built based on the error code and the error message. '''
def error_response(error_code : int, error_message : str):
    return {
        'code': error_code,
        'message': error_message
    }