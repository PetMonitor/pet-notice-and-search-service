from http import HTTPStatus
from src.main.app import app
from mock import patch

from src.main.constants import DATABASE_SERVER_URL

class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0
        self.content = None
        self.raw = None

        if (self.url == DATABASE_SERVER_URL + "/photos/profile/123"):
            self.status_code = 200
            self.content = bytes("someImgFile", "utf-8")
        elif (self.url == DATABASE_SERVER_URL + "/photos/456"):
            self.status_code = 200
            self.content = bytes("someOtherImgFile", "utf-8")    
        else:
            self.status_code = 404
            self.response = {"error":"test route not found"}            
    
    def raise_for_status(self):
        return

    def response(self):
        return self.response


class TestPhoto(object):

    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_photo_returns_photo(self, fake_get):
        client = app.test_client()
        response = client.get('/api/v0/photos/456')
        assert response.status_code == HTTPStatus.OK
        assert response.get_data() == bytes("someOtherImgFile", "utf-8")   

class TestUserProfilePicture(object):

    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_profile_picture_returns_picture(self, fake_get):
        client = app.test_client()
        response = client.get('/api/v0/photos/profile/123')
        assert response.status_code == HTTPStatus.OK
        assert response.get_data() == bytes("someImgFile", "utf-8")
