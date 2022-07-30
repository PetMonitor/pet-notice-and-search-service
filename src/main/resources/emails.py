import requests
from http import HTTPStatus

from flask_restful import request, Resource

from src.main.constants import DATABASE_SERVER_URL

BASE_EMAIL = DATABASE_SERVER_URL + "/emails"
BASE_CONFIRMATION_EMAIL_URL = DATABASE_SERVER_URL + "/emails/confirmation"

class ConfirmationEmail(Resource):
    def post(self):
        try:
            sendEmailConfirmationData = request.get_json()
            print("Sending confirmation email to {}".format(sendEmailConfirmationData))

            response = requests.post(BASE_CONFIRMATION_EMAIL_URL, sendEmailConfirmationData)
            response.raise_for_status()
            return "OK", HTTPStatus.CREATED

        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  


class ConfirmationEmailCheck(Resource):
    def post(self):  
        try:
            print("Checking email confirmed")
            checkEmailCondirmedUrl = BASE_CONFIRMATION_EMAIL_URL + "/check"
            checkEmailConfirmationData = request.get_json()

            response = requests.post(checkEmailCondirmedUrl, checkEmailConfirmationData)
            
            return response.json(), HTTPStatus.OK
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  

class Emails(Resource):
    def post(self):
        try:
            sendEmailData = request.get_json()
            print("Sending email to {}".format(sendEmailData['sendTo']))

            response = requests.post(BASE_EMAIL, sendEmailData)

            if response.status_code == HTTPStatus.NOT_FOUND:
                return response.json()['error'], HTTPStatus.NOT_FOUND

            if response.status_code == HTTPStatus.BAD_REQUEST:
                return "Bad request: {}".format(response.json()['error']), HTTPStatus.NOT_FOUND
            response.raise_for_status()
            return "OK", HTTPStatus.CREATED 
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR              