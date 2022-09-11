import json
from http import HTTPStatus
from src.main.app import app
from mock import patch

from src.main.constants import DATABASE_SERVER_URL

class FakePost(object):
    def __init__(self, url, headers={}, json=''):
        self.url = url
        self.db = DATABASE_SERVER_URL
        self.data = json
        self.status_code = 0

        if (self.url == DATABASE_SERVER_URL + "/emails"):
            self.status_code = HTTPStatus.CREATED
            self.response = { "created": 1 }
        elif (self.url == DATABASE_SERVER_URL + "/emails/confirmation"):
            self.status_code = HTTPStatus.CREATED
            self.response = { "cancelled": 1 }
        elif (self.url == DATABASE_SERVER_URL + "/emails/confirmation/check"):
            self.status_code = HTTPStatus.CREATED
            self.response = { "cancelled": 1 }    
        else:
            self.response = { "code" : 404, "message" : "Not Found" }

    def json(self):
        return self.response       

    def raise_for_status(self):
        if self.status_code != HTTPStatus.CREATED:
            raise ValueError("Database mock server returned error {}".format(self.status_code))


class TestEmails(object):

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_send_email(self, fake_post):
        testSendEmailReq = { 'sendTo': 'euge@gmail.com' }

        client = app.test_client()
        response = client.post('/api/v0/emails', json=testSendEmailReq)
        assert response.status_code == HTTPStatus.CREATED

class TestConfirmationEmail(object):

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_send_confirmation_email(self, fake_post):
        testConfirmationEmailReq = { 'emailAddress': 'euge@gmail.com' }

        client = app.test_client()
        response = client.post('/api/v0/emails/confirmation', json=testConfirmationEmailReq)
        assert response.status_code == HTTPStatus.CREATED

class TestConfirmationEmailCheck(object):

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_check_confirmation_email(self, fake_post):
        testCheckConfirmationEmailReq = { 'emailAddress': 'euge@gmail.com' }

        client = app.test_client()
        response = client.post('/api/v0/emails/confirmation/check', json=testCheckConfirmationEmailReq)
        assert response.status_code == HTTPStatus.OK
