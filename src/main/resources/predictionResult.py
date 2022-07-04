import json
import requests
from http import HTTPStatus

from cerberus import Validator
from flask_restful import request, Resource

from src.main.constants import DATABASE_SERVER_URL
from src.main.utils.requestAuthorizer import RequestAuthorizer

class PredictionResult(Resource):

    def __init__(self):
        # Argument validator for User methods' JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(PredictionResult, self).__init__()

    
    def post(self, searchedNoticeId):
        """
        Creates a new feedback record for prediction.
        """
        try:
            print('Providing feedback for searched notice {}'.format(searchedNoticeId))
            predictedNotices = request.get_json()
            response = requests.post(DATABASE_SERVER_URL + "/prediction/result/failure/" + searchedNoticeId, headers={'Content-Type': 'application/json'}, data=json.dumps(predictedNotices))

            response.raise_for_status()
            return response.json(), HTTPStatus.CREATED
        except Exception as e:
            print("Failed to create feedback: {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR
    