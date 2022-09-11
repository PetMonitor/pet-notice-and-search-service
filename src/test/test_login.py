import json
from http import HTTPStatus
from src.main.app import app
from mock import patch

from src.main.constants import DATABASE_SERVER_URL

TEST_USER_CREDENTIALS = {
    "username": "tpratchett",
    "password": "discworld123"
}

TEST_INCORRECT_USER_CREDENTIALS = {
    "username": "neilgaiman",
    "password": "coraline123"
}

TEST_SESSION_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiMTIzZTQ1NjctZTg5Yi0xMmQzLWE0NTYtNDI2NjE0MTc0MDAwIiwiX3JlZiI6ImU2ZWJlZDBiLTgwM2MtNDNiZS1iYWFmLWQzNzBiYzRlMDdmMCIsInVzZXJuYW1lIjoiVGVycnlQcmF0Y2hldHQiLCJlbWFpbCI6InRlcnJ5cHJhdGNoZXR0QGRpc2N3b3JsZC5jb20iLCJuYW1lIjoiVGVycnkgUHJhdGNoZXR0In0.X94eZgQmUIHp_M_IWyc1uCE2VIaG0TptK2MDSpyMaIo"


class FakePost(object):
    def __init__(self, url, headers={}, json=''):
        self.url = url
        self.db = DATABASE_SERVER_URL
        self.data = json
        self.status_code = 0

        if (self.url == DATABASE_SERVER_URL + "/users/credentialValidation" and "username" in self.data and self.data["username"] == TEST_USER_CREDENTIALS["username"]):
            self.status_code = HTTPStatus.CREATED
            self.response = {
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "_ref": "e6ebed0b-803c-43be-baaf-d370bc4e07f0",
                "username": "TerryPratchett",
                "email": "terrypratchett@discworld.com",
                "name": "Terry Pratchett"
            }
        elif ("username" in self.data and self.data["username"] == TEST_INCORRECT_USER_CREDENTIALS["username"]):
            self.status_code = HTTPStatus.UNAUTHORIZED
            self.response = { "message": "incorrect credentials" }
        else:
            self.response = { "code" : 404, "message" : "Not Found" }

    def json(self):
        return self.response       

    def raise_for_status(self):
        if self.status_code != HTTPStatus.CREATED:
            raise ValueError("Database mock server returned error {}".format(self.status_code))




class TestUserLogin(object):
    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_user_login_request(self, fake_post):    
        response = app.test_client().post('/api/v0/users/login', json=TEST_USER_CREDENTIALS)

        assert response.status_code == HTTPStatus.OK
        assert response.get_json()["sessionToken"] == TEST_SESSION_TOKEN

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_user_login_request_with_incorrect_credentials(self, fake_post):    
        response = app.test_client().post('/api/v0/users/login', json=TEST_INCORRECT_USER_CREDENTIALS)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
