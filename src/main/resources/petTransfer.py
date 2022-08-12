import uuid
import requests

from http import HTTPStatus
from cerberus import Validator

from flask_restful import fields, request, Resource, marshal

from src.main.constants import DATABASE_SERVER_URL


transfer_fields = {
    'uuid': fields.String(attribute='uuid'),
    '_ref': fields.String,
    'petId': fields.String,
    'transferFromUser': fields.String,
    'transferToUser': {
        'volunteerData': {
            'userId': fields.String(attribute='transferToUser.volunteerData.userId'),
            'petTypesToFoster': fields.List(fields.String, attribute='transferToUser.volunteerData.petTypesToFoster'),
            'petSizesToFoster': fields.List(fields.String, attribute='transferToUser.volunteerData.petSizesToFoster'),
            'province': fields.String(attribute='transferToUser.volunteerData.province'),
            'location': fields.String(attribute='transferToUser.volunteerData.location'),
            'averageRating': fields.Integer(attribute='transferToUser.volunteerData.averageRating')
        },
        'username': fields.String(attribute='transferToUser.username'),
        'name': fields.String(attribute='transferToUser.name'),
    },
    'activeFrom': fields.String,
    'activeUntil': fields.String,
    'cancelled': fields.Boolean,
    'completedOn': fields.String,
}

class PetTransfer(Resource):

    PET_TRANSFER_SCHEMA = {
        "uuid": {"type": "string", "required": True},
        "_ref": {"type": "string", "required": True},
        "transferToUser": {
            "type": "string", 
            "required": True,
        },
    }

    def __init__(self):
        # Argument parser for PetTransfer creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(PetTransfer, self).__init__()

    def get(self, petId):
        """
        Retrieves all the active transfers for pet.
        :param petId identifier of the pet whose transfers will be retrieved.
        """
        try:
            transferURL = DATABASE_SERVER_URL + "/pets/" + petId + "/transfer"
            print("Issue GET to " + transferURL)
            response = requests.get(transferURL)
            if response:
                response.raise_for_status()
                return marshal(response.json(), transfer_fields), HTTPStatus.OK
            return "No transfer found.", HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


    def post(self, petId):
        """
        Creates a new pet transference process.
        :param petId identifier of the pet to be transfered.
        """
        try:
            transferURL = DATABASE_SERVER_URL + "/pets/" + petId + "/transfer"
            print("Issue POST to " + transferURL)

            petTransferData = request.get_json()
            petTransferData["uuid"] = str(uuid.uuid4())
            petTransferData["_ref"] = str(uuid.uuid4())
            if not self.arg_validator.validate(petTransferData, PetTransfer.PET_TRANSFER_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Transfer pet entry failed, received invalid data {} for pet {}: {}".format(petTransferData, petId,
                                                                                     self.arg_validator.errors), HTTPStatus.BAD_REQUEST
            response = requests.post(transferURL, json=petTransferData)

            try:
                response.raise_for_status()
                return response.json(), HTTPStatus.CREATED
            except requests.exceptions.RequestException as e:
                print("ERROR {}".format(e))
                return "ERROR {}".format(e), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

class PetTransferCancellation(Resource):

    def __init__(self):
        # Argument parser for PetTransferCancellation creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(PetTransferCancellation, self).__init__()

    def post(self, petId, transferId):
        """
        Creates a new pet transference process.
        :param petId identifier of the pet to be transfered.
        :param transferenceId identifier of the transfer operation to be cancelled.
        """
        try:
            transferCancellationURL = DATABASE_SERVER_URL + "/pets/" + petId + "/transfer/" + transferId + "/cancel"
            print("Issue POST to " + transferCancellationURL)

            response = requests.post(transferCancellationURL)

            try:
                response.raise_for_status()
                return response.json(), HTTPStatus.CREATED
            except requests.exceptions.RequestException as e:
                print("ERROR {}".format(e))
                return "ERROR {}".format(e), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR