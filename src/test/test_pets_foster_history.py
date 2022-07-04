import json
from http import HTTPStatus
from mock import patch
from src.main.app import app
'''
class TestPetsFosterHistory(object):

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

'''