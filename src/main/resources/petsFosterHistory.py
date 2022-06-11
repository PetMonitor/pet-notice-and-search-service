import uuid
import requests

from http import HTTPStatus
from cerberus import Validator

from flask_restful import fields, request, Resource, marshal

from src.main.constants import DATABASE_SERVER_URL


# Fields returned by the src for PetFosterHistory resource
history_fields = {
    'historyId': fields.String(attribute='uuid'),
    '_ref': fields.String,
    'petId': fields.String,
    'userId': fields.String,
    'contactEmail': fields.String,
    'contactPhone': fields.String,
    'contactName': fields.String,
    'sinceDate': fields.String,
    'untilDate': fields.String,
}


class PetFosterHistoryEntry(Resource):

    PET_FOSTER_HISTORY_ENTRY_SCHEMA = {
        "_ref": {"type": "string", "required": True},
        "petId": {"type": "string"},
        "userId": {"type": "string", 'nullable': True},
        "contactEmail": {"type": "string"},
        "contactPhone": {"type": "string"},
        "contactName": {"type": "string"},
        "sinceDate": {'type': 'string'},
        "untilDate": {'type': 'string'}
    }

    def __init__(self):
        # Argument parser for PetFosterHistory entry creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(PetFosterHistoryEntry, self).__init__()

    def get(self, petId, historyId):
        """
        Retrieves a pet foster history entry by id.
        :param petId identifier of the pet whose history will be retrieved.
        :param historyId identifier of the entry that will be retrieved.
        """
        try:
            historyByIdURL = DATABASE_SERVER_URL + "/pets/" + petId + "/fosterHistory/" + historyId
            print("Issue GET to " + historyByIdURL)
            response = requests.get(historyByIdURL)
            if response:
                response.raise_for_status()
                return marshal(response.json(), history_fields), HTTPStatus.OK
            return "No history found for pet id {}, history entry id".format(petId, historyId), HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

    def put(self, petId, historyId):
        """
        Updates the pet foster history entry of a pet.
        :param petId identifier of the pet whose history will be updated.
        :param historyId identifier of the entry that will be updated.
        :returns the updated history.
        """
        try:
            historyByIdURL = DATABASE_SERVER_URL + "/pets/" + petId + "/fosterHistory/" + historyId
            print("Issue PUT to " + historyByIdURL)
            updatedHistoryEntry = request.get_json()
            if not self.arg_validator.validate(updatedHistoryEntry,
                                               PetFosterHistoryEntry.PET_FOSTER_HISTORY_ENTRY_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Received invalid history entry for update {}: {}".format(updatedHistoryEntry, self.arg_validator.errors), HTTPStatus.BAD_REQUEST

            response = requests.put(historyByIdURL, json=updatedHistoryEntry)
            if response:
                response.raise_for_status()
                return marshal(response.json(), history_fields), HTTPStatus.OK
            return "Received empty response from database server. History with id {} from pet {} could not be updated.".format(historyId, petId), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return "ERROR {}".format(e), HTTPStatus.INTERNAL_SERVER_ERROR

    def delete(self, petId, historyId):
        """
        Deletes a history entry from a pet.
        :param petId identifier of the pet whose history will be deleted.
        :param historyId identifier of the entry that will be deleted.
        """
        try:
            historyByIdURL = DATABASE_SERVER_URL + "/pets/" + petId + "/fosterHistory/" + historyId
            print("Issue DELETE to " + historyByIdURL)
            response = requests.delete(historyByIdURL)
            if response:
                response.raise_for_status()
                return "Successfully deleted {} records".format(response.json()), HTTPStatus.OK
        except Exception as e:
            print("Failed to delete history {} from pet {}: {}".format(historyId, petId, e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR


class PetFosterHistory(Resource):

    PET_FOSTER_HISTORY_ENTRY_SCHEMA = {
        "uuid": {"type": "string", "required": True},
        **PetFosterHistoryEntry.PET_FOSTER_HISTORY_ENTRY_SCHEMA
    }

    def __init__(self):
        # Argument parser for PetFosterHistory creation's JSON body
        self.arg_validator = Validator()
        self.arg_validator.allow_unknown = False
        super(PetFosterHistory, self).__init__()

    def get(self, petId):
        """
        Retrieves all the pet's foster history entries.
        :param petId identifier of the pet whose history will be retrieved.
        """
        try:
            historyURL = DATABASE_SERVER_URL + "/pets/" + petId + "/fosterHistory"
            print("Issue GET to " + historyURL)
            response = requests.get(historyURL)
            if response:
                response.raise_for_status()
                return marshal(response.json(), history_fields), HTTPStatus.OK
            return "No history found.", HTTPStatus.NOT_FOUND
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR

    def post(self, petId):
        """
        Creates a foster history entry for a pet.
        :param petId identifier of the pet whose history will be created.
        :returns the new history entry.
        """
        try:
            historyURL = DATABASE_SERVER_URL + "/pets/" + petId + "/fosterHistory"
            print("Issue POST to " + historyURL)

            newHistory = request.get_json()
            newHistory["uuid"] = str(uuid.uuid4())
            newHistory["_ref"] = str(uuid.uuid4())
            if not self.arg_validator.validate(newHistory, PetFosterHistory.PET_FOSTER_HISTORY_ENTRY_SCHEMA):
                print("ERROR {}".format(self.arg_validator.errors))
                return "Create foster history entry failed, received invalid history {} for pet {}: {}".format(newHistory, petId,
                                                                                     self.arg_validator.errors), HTTPStatus.BAD_REQUEST
            response = requests.post(historyURL, json=newHistory)
            try:
                response.raise_for_status()
                return marshal(response.json(), history_fields), HTTPStatus.CREATED
            except requests.exceptions.RequestException as e:
                print("ERROR {}".format(e))
                return "ERROR {}".format(e), HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR
