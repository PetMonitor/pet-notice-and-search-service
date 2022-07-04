import json
from http import HTTPStatus
from multiprocessing.sharedctypes import Value
from mock import patch
from src.main.app import app

DATABASE_URL = "http://127.0.0.1:8000/fosterVolunteerProfiles"
FOSTER_PROFILES_BASE_URL = "/api/v0/fosterVolunteerProfiles"

TEST_PROFILES = [
    {
        "uuid": "6271ef25-7f90-4c38-95a1-68661a0066be",
        "_ref": "c7f769c0-3774-45b6-9b17-37960c5e1089",
        "userId": "187a8a8a-f80a-4581-8e23-07cf8a6b1719",
        "petTypesToFoster": ["DOG", "CAT"],
        "petSizesToFoster": ["SMALL"],
        "additionalInformation": "",
        "location": "Belgrano",
        "province": "Buenos Aires",
        "available": True,
        "averageRating": 3.7,
        "ratingAmount": 4,
    },
    {
        "uuid": "d3ab1c7f-9c88-48ca-be36-aaeceb578cc4",
        "_ref": "a25e6815-4a22-4e82-9016-19ea39fdc69a",
        "userId": "221d90ad-638e-426d-bd71-cc6bc00acfda",
        "petTypesToFoster": ["CAT"],
        "petSizesToFoster": ["SMALL"],
        "additionalInformation": "",
        "location": "Palermo",
        "province": "Buenos Aires",
        "available": True,
        "averageRating": 3.9,
        "ratingAmount": 4,
    },
]

TEST_PROFILES_OUTPUT = [
    {
        "profileId": "6271ef25-7f90-4c38-95a1-68661a0066be",
        "_ref": "c7f769c0-3774-45b6-9b17-37960c5e1089",
        "userId": "187a8a8a-f80a-4581-8e23-07cf8a6b1719",
        "petTypesToFoster": ["DOG", "CAT"],
        "petSizesToFoster": ["SMALL"],
        "additionalInformation": "",
        "location": "Belgrano",
        "province": "Buenos Aires",
        "available": True,
        "averageRating": 3.7,
        "ratingAmount": 4,
    },
    {
        "profileId": "d3ab1c7f-9c88-48ca-be36-aaeceb578cc4",
        "_ref": "a25e6815-4a22-4e82-9016-19ea39fdc69a",
        "userId": "221d90ad-638e-426d-bd71-cc6bc00acfda",
        "petTypesToFoster": ["CAT"],
        "petSizesToFoster": ["SMALL"],
        "additionalInformation": "",
        "location": "Palermo",
        "province": "Buenos Aires",
        "available": True,
        "averageRating": 3.9,
        "ratingAmount": 4,
    },
]

class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url == DATABASE_URL + "?queryparam=1"):
            self.status_code = 200
            self.response = TEST_PROFILES
        elif (self.url == DATABASE_URL + '/' + TEST_PROFILES[0]['uuid']):
            self.status_code = 200
            self.response = TEST_PROFILES[0]
        else:
            self.status_code = 404
            self.response = {"error":"test route not found"}            

    def json(self):
        return self.response
    
    def raise_for_status(self):
        return

    def response(self):
        return self.response

class FakeGetError(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url == DATABASE_URL):
            self.status_code = 500

    def raise_for_status(self):
        raise ValueError("Error from database server!!")

class TestFosterVolunteerProfile(object):


    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_all_volunteer_profiles_returns_all_profiles(self, fake_get):
        response = app.test_client().get(FOSTER_PROFILES_BASE_URL + "?queryparam=1")

        responseBody = response.get_json()

        # Verify response content 
        assert len(responseBody) == len(TEST_PROFILES_OUTPUT)
        for i in range(len(TEST_PROFILES_OUTPUT)):
            assert responseBody[i]== TEST_PROFILES_OUTPUT[i]
        assert response.status_code == HTTPStatus.OK

    @patch("src.main.resources.user.requests.get", side_effect=FakeGetError)
    def test_get_profiles_returns_error_if_server_fails(self, fake_get_error):
        response = app.test_client().get(FOSTER_PROFILES_BASE_URL + "?queryparam=1")

        responseBody = response.get_json()

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR    


    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_volunteer_profiles_by_id_returns_profile(self, fake_get):
        response = app.test_client().get(FOSTER_PROFILES_BASE_URL + "/" + TEST_PROFILES[0]["uuid"])

        responseBody = response.get_json()

        # Verify response content 
        assert len(responseBody) == len(TEST_PROFILES_OUTPUT[0])
        assert responseBody == TEST_PROFILES_OUTPUT[0]
        assert response.status_code == HTTPStatus.OK    