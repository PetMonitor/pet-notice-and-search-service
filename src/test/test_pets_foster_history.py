import json
from http import HTTPStatus
from mock import patch
from src.main.app import app

DATABASE_URL = "http://127.0.0.1:8000/pets/6271ef25-7f90-4c38-95a1-68661a0066be/fosterHistory"

TEST_HISTORIES = [
    {
        "uuid": "6271ef25-7f90-4c38-95a1-68661a0066be",
        "_ref": "c7f769c0-3774-45b6-9b17-37960c5e1089",
        "petId": "d3ab1c7f-9c88-48ca-be36-aaeceb578cc4",
        "userId": "a25e6815-4a22-4e82-9016-19ea39fdc69a",
        "contactEmail": "galgut@gmail.com",
        "contactPhone": "222-000-666",
        "contactName": "Galgut",
        "sinceDate": "10-10-2021",
        "untilDate": "15-03-2022",
    },
    {
        "uuid": "6271ef25-7f90-4c38-95a1-68661a0077ca",
        "_ref": "c7f769c0-3774-45b6-9b17-37960c5e1077",
        "petId": "d3ab1c7f-9c88-48ca-be36-aaeceb578aa4",
        "userId": "a25e6815-4a22-4e82-9016-19ea39fdc88a",
        "contactEmail": "ursulaleguin@gmail.com",
        "contactPhone": "222-000-777",
        "contactName": "Ursula K Le Guin",
        "sinceDate": "11-08-2021",
        "untilDate": "12-01-2022",
    },
]

class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url == DATABASE_URL):
            self.status_code = 200
            self.response = TEST_HISTORIES
        elif (self.url == DATABASE_URL + '/' + TEST_HISTORIES[0]['uuid']):
            self.status_code = 200
            self.response = TEST_HISTORIES[0]
        else:
            self.status_code = 404
            self.response = {"error":"test route not found"}            

    def json(self):
        return self.response
    
    def raise_for_status(self):
        return

    def response(self):
        return self.response

class FakeError(object):
	def __init__(self, url, headers={}, json=''):
		self.url = url
		self.data = json
		self.status_code = 500
		self.response = { "message" : "Internal Server Error" }

	def json(self):
		return self.response   

	def raise_for_status(self):
		raise ValueError("Database mock server returned error {}".format(self.status_code))

class FakeDelete(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.db = DATABASE_URL
		self.status_code = 0

		if (self.url == DATABASE_URL + "/" + TEST_HISTORIES[0]["uuid"]):
			self.status_code = 200
			self.response = { "code" : self.status_code, "deletedCount": 1 }         
		else:
			self.response = { "code" : 404, "message" : "Not Found" }

	def json(self):
		return self.response["deletedCount"]
           
	def raise_for_status(self):
		if self.status_code != HTTPStatus.OK:
			raise ValueError("Database mock server returned error {}".format(self.status_code))


class TestPetsFosterHistory(object):

    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_histories_returns_all_histories(self, fake_get):
        client = app.test_client()
        response = client.get('/api/v0/pets/6271ef25-7f90-4c38-95a1-68661a0066be/fosterHistory')

        responseBody = response.get_json()

        # Verify response content 
        assert len(responseBody) == len(TEST_HISTORIES)

        for i in range(len(TEST_HISTORIES)):
            responseBodyCopy = responseBody[i].copy()
            responseBodyCopy["uuid"] = responseBodyCopy["historyId"]
            del responseBodyCopy["historyId"]
            assert responseBodyCopy == TEST_HISTORIES[i]
        assert response.status_code == HTTPStatus.OK

    @patch("src.main.resources.user.requests.get", side_effect=FakeError)
    def test_get_histories_fails_if_server_request_fails(self, fake_get_error):
        client = app.test_client()
        response = client.get("/api/v0/pets/6271ef25-7f90-4c38-95a1-68661a0066be/fosterHistory")

        # Verify response content 
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR        

    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_history_by_id_returns_requested_history(self, fake_get):
        client = app.test_client()
        response = client.get("/api/v0/pets/6271ef25-7f90-4c38-95a1-68661a0066be/fosterHistory/" + TEST_HISTORIES[0]["uuid"])

        responseBody = response.get_json()

        # Verify response content 
        assert len(responseBody) == len(TEST_HISTORIES[0])

        responseBodyCopy = responseBody.copy()
        responseBodyCopy["uuid"] = responseBodyCopy["historyId"]
        del responseBodyCopy["historyId"]
        
        assert responseBodyCopy == TEST_HISTORIES[0]
        assert response.status_code == HTTPStatus.OK

    @patch("src.main.resources.user.requests.get", side_effect=FakeError)
    def test_get_history_by_id_fails_if_server_request_fails(self, fake_get_error):
        client = app.test_client()
        response = client.get("/api/v0/pets/6271ef25-7f90-4c38-95a1-68661a0066be/fosterHistory/" + TEST_HISTORIES[0]["uuid"])

        # Verify response content 
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR        

    @patch("src.main.resources.user.requests.delete", side_effect=FakeDelete)
    def test_delete_history_succeeds(self, fake_delete):
        client = app.test_client()
        response = client.delete("/api/v0/pets/6271ef25-7f90-4c38-95a1-68661a0066be/fosterHistory/" + TEST_HISTORIES[0]["uuid"])

        # Verify response content 
        assert response.status_code == HTTPStatus.OK 
        assert "Successfully deleted 1 records" in response.data.decode('utf-8')     

    @patch("src.main.resources.user.requests.delete", side_effect=FakeError)
    def test_delete_history_fails_if_server_request_fails(self, fake_delete_error):
        client = app.test_client()
        response = client.delete("/api/v0/pets/6271ef25-7f90-4c38-95a1-68661a0066be/fosterHistory/" + TEST_HISTORIES[0]["uuid"])

        # Verify response content 
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


#TODO: add post tests
#TODO: add put tests