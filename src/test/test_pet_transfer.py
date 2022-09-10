import json
from http import HTTPStatus
from src.main.app import app
from mock import patch

from src.main.constants import DATABASE_SERVER_URL


TEST_TRANSFER =  {
    'uuid': 'f378200f-fe18-4f61-8661-aadd55e1c622',
    '_ref': 'acb3008c-7a5e-4ae0-a8cd-d82f5223140a',
    'petId': '7d7a207d-ce16-4f87-8fce-badf18da00e8',
    'transferFromUser': 'e032421b-3edd-45b5-ab01-46f662aeecad',
    'transferToUser': {
        'volunteerData': {
            'userId': 'ddc9db6d-c416-45e3-9c72-2a1fb4f106cb',
            'petTypesToFoster': [ 'DOG' ],
            'petSizesToFoster': [ 'SMALL' ],
            'province': 'Buenos Aires',
            'location': 'CABA',
            'averageRating': 2
        },
        'username': 'tpratchett123',
        'name': 'terry',
    },
    'activeFrom': '01-10-2022',
    'activeUntil': '16-10-2022',
    'cancelled': False,
    'completedOn': None,
}

class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url == DATABASE_SERVER_URL + "/pets/123/transfer"):
            self.status_code = 200
            self.response = TEST_TRANSFER
        else:
            self.status_code = 404
            self.response = {"error":"test route not found"}            

    def json(self):
        return self.response
    
    def raise_for_status(self):
        return

    def response(self):
        return self.response

class FakePost(object):
    def __init__(self, url, headers={}, json=''):
        self.url = url
        self.db = DATABASE_SERVER_URL
        self.data = json
        self.status_code = 0

        if (self.url == DATABASE_SERVER_URL + "/pets/123/transfer"):
            self.status_code = HTTPStatus.CREATED
            self.response = { "created": 1 }
        elif (self.url.startswith(DATABASE_SERVER_URL + "/pets/123/transfer/456/cancel")):
            self.status_code = HTTPStatus.CREATED
            self.response = { "cancelled": 1 }
        else:
            self.response = { "code" : 404, "message" : "Not Found" }

    def json(self):
        return self.response       

    def raise_for_status(self):
        if self.status_code != HTTPStatus.CREATED:
            raise ValueError("Database mock server returned error {}".format(self.status_code))


class TestPetTransfer(object):

    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_pet_transfers_by_id_returns_transfer(self, fake_get):
        response = app.test_client().get('/api/v0/pets/123/transfer')

        assert response.status_code == HTTPStatus.OK

        responseBody = response.get_json()
        assert len(responseBody) == len(TEST_TRANSFER)
        assert json.dumps(responseBody, sort_keys=True) == json.dumps(TEST_TRANSFER, sort_keys=True)

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_post_pet_transfer_creates_sends_transfer_request(self, fake_post):
        testTransferRequest = {
            "transferToUser": 'ddc9db6d-c416-45e3-9c72-2a1fb4f106cb',
        }

        client = app.test_client()
        response = client.post('/api/v0/pets/123/transfer', json=testTransferRequest)
        assert response.status_code == HTTPStatus.CREATED


class TestPetTransferCancellation(object):

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_post_pet_transfer_creates_sends_transfer_request(self, fake_post):
        client = app.test_client()
        response = client.post('/api/v0/pets/123/transfer/456/cancel')
        assert response.status_code == HTTPStatus.CREATED
