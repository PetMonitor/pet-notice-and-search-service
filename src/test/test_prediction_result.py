import json
from http import HTTPStatus

from mock import patch

from src.main.app import app

DATABASE_URL = "http://127.0.0.1:8000/prediction/result/failure"

test_client = app.test_client()

PREDICTED_NOTICES = {
    "predictedNoticeIds": [ "123e4567-e89b-12d3-a456-426614175555", "123e4567-e89b-12d3-a456-426614176666" ]
}

NOTICE_ID = "123e4567-e89b-12d3-a456-426614175552"

class FakePost(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = DATABASE_URL
		self.data = data
		self.status_code = 0

		if (self.url == DATABASE_URL + "/" + NOTICE_ID):
			self.status_code = 201
			self.response = { "code" : self.status_code, "predictedNoticeIds": json.loads(self.data) }            
		else:
			self.response = { "code" : 404, "message" : "Not Found" }

	def json(self):
		return self.response["predictedNoticeIds"]        

	def raise_for_status(self):
		if self.status_code != HTTPStatus.CREATED:
			raise ValueError("Database mock server returned error {}".format(self.status_code))

class TestPredictionResult(object):

    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    def test_prediction_results_failure_returns_ok(self, fake_post):
        response = test_client.post('/api/v0/prediction/result/failure/' + NOTICE_ID, json=PREDICTED_NOTICES)
        assert response.status_code == HTTPStatus.CREATED

