import json
from http import HTTPStatus
from mock import patch
from src.main.app import app

DATABASE_URL = "http://127.0.0.1:8000/users"

TEST_USERS = [{
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "_ref": "e6ebed0b-803c-43be-baaf-d370bc4e07f0",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com",
    "name": "Terry Pratchett",
    "phoneNumber": "222-000-666",
    "profilePicture": None,
    "alertsActivated": True,
    "alertRadius": 1
}]

TEST_USERS_OUTPUT = [{
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "_ref": "e6ebed0b-803c-43be-baaf-d370bc4e07f0",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com",
    "name": "Terry Pratchett",
    "phoneNumber": "222-000-666",
    "profilePicture": None,
    "alertsActivated": True,
    "alertRadius": 1
}]

TEST_NEW_USER_NO_PETS = {
    "userId":  "123e4567-e89b-12d3-a456-426614174000",
    "_ref": "123e4567-e89b-12d3-a456-426614174000",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com",
    "name": "Terry Pratchett",
    "phoneNumber": "",
    "alertsActivated": False,
    "alertRadius": -1,
    "profilePicture": "base64EncodedImg"
}


"""
This mock classes are to override User and Users requests methods.
With the @patch decorator it is possible to make request.get() return
the next fake object; so it can perform an url check and mutate
to simulate different endpoints.
"""
class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url == DATABASE_URL):
            self.status_code = 200
            self.response = TEST_USERS
        elif (self.url == DATABASE_URL + '/' + TEST_USERS[0]['uuid']):
            self.status_code = 200
            self.response = TEST_USERS[0]
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

class FakePost(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = DATABASE_URL
		self.data = data
		self.status_code = 0

		if (self.url == DATABASE_URL):
			self.status_code = 201
			self.response = { "code" : self.status_code, "user": json.loads(self.data) }            
		else:
			self.response = { "code" : 404, "message" : "Not Found" }

	def json(self):
		return self.response["user"]        

	def raise_for_status(self):
		if self.status_code != HTTPStatus.CREATED:
			raise ValueError("Database mock server returned error {}".format(self.status_code))

class FakeDelete(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.db = DATABASE_URL
		self.status_code = 0

		if (self.url == DATABASE_URL + "/123"):
			self.status_code = 200
			self.response = { "code" : self.status_code, "deletedCount": 1 }         
		else:
			self.response = { "code" : 404, "message" : "Not Found" }

	def json(self):
		return self.response 
           
	def raise_for_status(self):
		if self.status_code != HTTPStatus.OK:
			raise ValueError("Database mock server returned error {}".format(self.status_code))

class FakePut(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = DATABASE_URL
		self.status_code = 0

		if (self.url == DATABASE_URL + "/123"):
			self.status_code = 200
			self.response = { "code" : self.status_code, "updatedCount": 1  }         
		elif (self.url == DATABASE_URL + "/123/password"):
			self.status_code = 200
			self.response = { "code" : self.status_code, "updatedCount": 1  }                 
		else:
			self.response = { "code" : 404, "message" : "Not Found" }

	def json(self):
		return self.response        

	def raise_for_status(self):
		if self.status_code != HTTPStatus.OK:
			raise ValueError("Database mock server returned error {}".format(self.status_code))


class TestUserRequests(object):

    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.isRequestAuthorized", return_value=True)
    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_users_returns_all_users(self, request_authorized_mock, fake_get):
        client = app.test_client()
        response = client.get('/api/v0/users')

        responseBody = json.loads(response.get_data())
        print("Test GET /users response: {}".format(str(responseBody)))

        # Verify response content 
        assert len(responseBody) == len(TEST_USERS_OUTPUT)
        for i in range(len(TEST_USERS_OUTPUT)):
            assert json.dumps(responseBody[i], sort_keys=True) == json.dumps(TEST_USERS_OUTPUT[i], sort_keys=True)
        assert response.status_code == HTTPStatus.OK


    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_user_by_id_returns_requested_user(self, request_authorized_mock, fake_get):
        client = app.test_client()
        response = client.get('/api/v0/users/' + TEST_USERS[0]['uuid'])

        responseBody = json.loads(response.get_data())

        # Verify response content 
        assert len(responseBody) == len(TEST_USERS_OUTPUT[0])
        assert json.dumps(responseBody, sort_keys=True) == json.dumps(TEST_USERS_OUTPUT[0], sort_keys=True)
        assert response.status_code == HTTPStatus.OK

    @patch("src.main.resources.user.requests.get", side_effect=FakeGetError)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    def test_get_user_by_id_returns_error_if_server_fails(self, request_authorized_mock, fake_get_error):
        client = app.test_client()
        response = client.get('/api/v0/users/' + TEST_USERS[0]['uuid'])

        # Verify response content 
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR    

    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=False)
    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    def test_get_user_by_id_unauthorized_fails(self, request_authorized_mock, fake_get):
        client = app.test_client()
        response = client.get('/api/v0/users/' + TEST_USERS[0]['uuid'])

        # Verify response content 
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_post_user_with_no_pets_creates_new_user(self, fake_post):
        createUserRequest =  {
            "username": "TerryPratchett",
            "name": "Terry Pratchett",
            "password": "verysercretpwd",
            "email": "terrypratchett@discworld.com",
            "profilePicture": "base64EncodedImg",
            "pets": []
        }

        client = app.test_client()
        response = client.post('/api/v0/users', json=createUserRequest)

        responseStatusCode = response.status_code
        createdUser = response.get_json()    

        assert responseStatusCode == HTTPStatus.CREATED
        assert  len(createdUser["userId"]) > 0
        assert  createdUser["email"] == TEST_NEW_USER_NO_PETS["email"]
        assert  createdUser["name"] == TEST_NEW_USER_NO_PETS["name"]

    
    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_post_user_with_pets_creates_new_user(self, fake_post):
        createUserRequest =  {
            "username": "TerryPratchett",
            "name": "Terry Pratchett",
            "password": "verysercretpwd",
            "email": "terrypratchett@discworld.com",
            "profilePicture": "base64EncodedImg",
            "pets": [{ 
                "type": "DOG", 
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "_ref": "123e4567-e89b-12d3-a456-426614175000",
                "name": "Greebo",
                "furColor": "brown",
                "size": "LARGE",
                "lifeStage": "PUPPY",
                "sex": "FEMALE",
                "breed": "",
                "isMyPet": True,
                "description": "This is greebo, he is my dog",
                "photos": [
                    "base64EncodedImg2",
                    "base64EncodedImg3"
                ]
            }]
        }

        client = app.test_client()
        response = client.post('/api/v0/users', json=createUserRequest)

        responseStatusCode = response.status_code
        createdUser = response.get_json()    
        
        print("CREATED PET WITH PETS {}".format(createdUser))
        assert responseStatusCode == HTTPStatus.CREATED
        assert  len(createdUser["userId"]) > 0
        assert  len(createdUser["_ref"]) > 0
        assert  createdUser["email"] == createUserRequest["email"]
        assert  createdUser["name"] == createUserRequest["name"]
    

    def test_post_user_if_req_missing_required_field_request_fails(self):
        createUserRequestMissingEmail =  {
            "username": "TerryPratchett",
            "name": "Terry Pratchett",
            "password": "verysercretpwd",
            "profilePicture": "base64EncodedImg",
            "pets": []
        }

        client = app.test_client()
        response = client.post('/api/v0/users', json=createUserRequestMissingEmail)

        responseStatusCode = response.status_code

        assert responseStatusCode == HTTPStatus.BAD_REQUEST

    def test_post_user_if_missing_both_pwd_and_facebookId_request_fails(self):
        createUserRequestMissingPwdAndFacebookId =  {
            "username": "TerryPratchett",
            "name": "Terry Pratchett",
            "email": "terrypratchett@discworld.com",
            "profilePicture": "base64EncodedImg",
            "pets": []
        }

        client = app.test_client()
        response = client.post('/api/v0/users', json=createUserRequestMissingPwdAndFacebookId)

        responseStatusCode = response.status_code

        assert responseStatusCode == HTTPStatus.BAD_REQUEST    

    @patch("src.main.resources.user.requests.delete", side_effect=FakeDelete)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    def test_delete_user_request_returns_ok(self, request_authorized_mock, fake_delete):
        deletedUserId = "123"

        client = app.test_client()
        response = client.delete('/api/v0/users/' + deletedUserId)

        assert response.status_code == HTTPStatus.OK
        assert "Successfully deleted 1 records" in response.data.decode('utf-8')

    @patch("src.main.resources.user.requests.delete", side_effect=FakeDelete)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=False)
    def test_delete_user_not_authorized_fails(self, request_authorized_mock, fake_delete):
        deletedUserId = "123"

        client = app.test_client()
        response = client.delete('/api/v0/users/' + deletedUserId)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @patch("src.main.resources.user.requests.put", side_effect=FakePut)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    def test_put_user_request_returns_ok(self, request_authorized_mock, fake_put):
        modifiedUserId = "123"
        modifiedUserRequest =  {
            "_ref": "234234",
            "username": "TerryPratchett",
            "name": "Terry Pratchett",
        }

        client = app.test_client()
        response = client.put('/api/v0/users/' + modifiedUserId, json=modifiedUserRequest)

        assert response.status_code == HTTPStatus.OK
        assert "Successfully updated 1 records" in response.data.decode('utf-8')    


    @patch("src.main.resources.user.requests.put", side_effect=FakePut)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    def test_put_user_request_missing_required_field_fails(self, request_authorized_mock, fake_put):
        modifiedUserId = "123"
        modifiedUserRequestNoRef =  {
            "username": "TerryPratchett",
            "name": "Terry Pratchett",
        }

        client = app.test_client()
        response = client.put('/api/v0/users/' + modifiedUserId, json=modifiedUserRequestNoRef)

        assert response.status_code == HTTPStatus.BAD_REQUEST

    @patch("src.main.resources.user.requests.put", side_effect=FakePut)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=False)
    def test_put_user_request_unauthorized_fails(self, request_authorized_mock, fake_put):
        modifiedUserId = "123"
        modifiedUserRequestNoRef =  {
            "username": "TerryPratchett",
            "name": "Terry Pratchett",
        }

        client = app.test_client()
        response = client.put('/api/v0/users/' + modifiedUserId, json=modifiedUserRequestNoRef)

        assert response.status_code == HTTPStatus.UNAUTHORIZED


    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    def test_get_user_contact_info_returns_contact_information(self, request_authorized_mock, fake_get):
        expectedContactInfo = {
            "userId": TEST_USERS[0]["uuid"],
            "name": TEST_USERS[0]["name"],
            "phoneNumber": TEST_USERS[0]["phoneNumber"],
            "email": TEST_USERS[0]["email"],
        }

        client = app.test_client()
        response = client.get('/api/v0/users/' + TEST_USERS[0]['uuid'] + '/contactInfo')

        userContactInfo = response.get_json()    

        assert response.status_code == HTTPStatus.OK
        assert userContactInfo == expectedContactInfo

    @patch("src.main.resources.user.requests.put", side_effect=FakePut)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    def test_user_change_pwd_returns_ok(self, request_authorized_mock, fake_put):
        modifiedUserId = "123"
        modifyUserPwdRequest =  {
            "_ref": "234234",
            "oldPassword": "discworld123",
            "newPassword": "goodOmens123",
        }

        client = app.test_client()
        response = client.put('/api/v0/users/' + modifiedUserId + '/password', json=modifyUserPwdRequest)

        assert response.status_code == HTTPStatus.OK
        assert "Successfully updated 1 records" in response.data.decode('utf-8')       

    @patch("src.main.resources.user.requests.put", side_effect=FakePut)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=True)
    def test_user_change_pwd_fails_if_required_field_not_provided(self, request_authorized_mock, fake_put):
        modifiedUserId = "123"
        modifyUserPwdRequest =  {
            "oldPassword": "discworld123",
            "newPassword": "goodOmens123",
        }

        client = app.test_client()
        response = client.put('/api/v0/users/' + modifiedUserId + '/password', json=modifyUserPwdRequest)

        assert response.status_code == HTTPStatus.BAD_REQUEST

    @patch("src.main.resources.user.requests.put", side_effect=FakePut)
    @patch("src.main.utils.requestAuthorizer.RequestAuthorizer.authenticateRequester", return_value=False)
    def test_user_change_pwd_not_authorized_returns_error(self, request_authorized_mock, fake_put):
        modifiedUserId = "123"
        modifyUserPwdRequest =  {
            "_ref": "234234",
            "oldPassword": "discworld123",
            "newPassword": "goodOmens123",
        }
        client = app.test_client()
        response = client.put('/api/v0/users/' + modifiedUserId + '/password', json=modifyUserPwdRequest)

        assert response.status_code == HTTPStatus.UNAUTHORIZED    

