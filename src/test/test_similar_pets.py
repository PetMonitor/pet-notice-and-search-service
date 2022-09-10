
from http import HTTPStatus
from src.main.app import app
from src.main.resources.similarPets import SimilarPetsAlerts

import unittest.mock as mock
from mock import patch, MagicMock

from mock import patch

from src.test.test_user import TEST_USERS


DATABASE_URL = "http://127.0.0.1:8000"
DATABASE_SIMILAR_PETS_URL = DATABASE_URL + "/similarPets" 
DATABASE_NOTIFICATIONS_URL = DATABASE_URL + "/notifications/notices/closestMatches"
DATABASE_SIMILAR_PETS_FINDER = DATABASE_URL + "/pets/finder/123?region=Birmingham"
DATABASE_SIMILAR_PETS_FINDER_EMPTY = DATABASE_URL + "/pets/finder/456?region=Birmingham"
CLOSEST_MATCHES_RESPONSE = {
    "closestMatches": [ "123e4567-e89b-12d3-a456-426614175555", "123e4567-e89b-12d3-a456-426614176666" ]
}

CLOSEST_MATCHES_EMPTY_RESPONSE = {
    "closestMatches": [ ]
}

class FakeScheduledJob(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

TEST_NOTICES_OUTPUT = [
      {
        "noticeId": "123e4567-e89b-12d3-a456-426614175555",
        "_ref": "447b86ea-b1c7-4e2a-a167-7542dcfbfd24",
        "pet": {"id":"123e4567-e89b-12d3-a456-426614174001", "photo": None},
        "userId": "123e4567-e89b-12d3-a456-426614174000",
        "noticeType": "LOST",
        "eventLocation": {"lat":123.0,"long": 345.0},
        "description": "My pet is lost! Please help!",
        "eventTimestamp": "2021-08-16T02:34:46+00:00",
        "street": "Green Ln",
        "neighbourhood": "Bovingdon",
        "locality": "Hertfordshire",
        "country": "England",
      },
      {
        "noticeId": "123e4567-e89b-12d3-a456-426614176666",
        "_ref": "05783c09-e5bb-4a47-8978-8c61b93ca545",
        "pet": {"id":"123e4567-e89b-12d3-a456-426614174002", "photo": None},
        "userId": "123e4567-e89b-12d3-a456-426614175000",
        "noticeType": "FOUND",
        "eventLocation": {"lat":123.0,"long": 345.0},
        "description": "I found this lovely dog!",
        "eventTimestamp": "2021-08-16T02:34:46+00:00",
        "street": "Green Ln",
        "neighbourhood": "Bovingdon",
        "locality": "Hertfordshire",
        "country": "England",
      }
]

TEST_SCHEDULED_JOBS = [FakeScheduledJob("123","testScheduledJob_123"), FakeScheduledJob("456", "testScheduledJob_456")]

class FakePost(object):
	def __init__(self, url, headers={}, data=''):
		self.url = url
		self.db = DATABASE_URL
		self.data = data
		self.status_code = 0

		if (self.url == DATABASE_NOTIFICATIONS_URL):
			self.status_code = 201
			self.response = { "code" : self.status_code }            
		else:
			self.response = { "code" : 404, "message" : "Not Found" }

	def json(self):
		return self.response["user"]        

	def raise_for_status(self):
		if self.status_code != HTTPStatus.CREATED:
			raise ValueError("Database mock server returned error {}".format(self.status_code))


class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url == DATABASE_SIMILAR_PETS_FINDER):
            self.status_code = 200
            self.response = CLOSEST_MATCHES_RESPONSE
        elif (self.url == DATABASE_SIMILAR_PETS_FINDER_EMPTY):
            self.status_code = 200
            self.response = CLOSEST_MATCHES_EMPTY_RESPONSE
        else:
            self.status_code = 404
            self.response = {"error":"test route not found"}            

    def json(self):
        return self.response
    
    def raise_for_status(self):
        return

    def response(self):
        return self.response

class TestSimilarPets(object):

  def test_get_similar_pets_returns_list_with_similar_notices(self, requests_mock):
      searchedNoticeId = "123e4567-e89b-12d3-a456-426614175552"
      requests_mock.get(DATABASE_URL + "/pets/finder/" + searchedNoticeId, json=CLOSEST_MATCHES_RESPONSE)
      requests_mock.get(DATABASE_URL + "/notices/" + CLOSEST_MATCHES_RESPONSE["closestMatches"][0], json=TEST_NOTICES_OUTPUT[0])
      requests_mock.get(DATABASE_URL + "/notices/" + CLOSEST_MATCHES_RESPONSE["closestMatches"][1], json=TEST_NOTICES_OUTPUT[1])

      response = app.test_client().get('/api/v0/similarPets/' + searchedNoticeId)
      assert response.status_code == HTTPStatus.OK

  @patch("src.main.resources.similarPets.BackgroundScheduler.get_jobs", side_effect=[TEST_SCHEDULED_JOBS])
  def test_get_similar_pets_alerts_returns_list_of_all_scheduled_alerts(self, requests_mock):
      response = app.test_client().get('/api/v0/similarPets/alerts')
      assert response.status_code == HTTPStatus.OK
      assert response.json == { "jobs": [
        { "id" : TEST_SCHEDULED_JOBS[0].id, "name": TEST_SCHEDULED_JOBS[0].name },
        { "id" : TEST_SCHEDULED_JOBS[1].id, "name": TEST_SCHEDULED_JOBS[1].name }
      ]}

  @patch.multiple(
    "src.main.resources.similarPets.BackgroundScheduler", 
    get_jobs=MagicMock(return_value=[]),
    add_job=MagicMock(return_value=None),
  )
  def test_post_similar_pets_alerts_schedules_programmed_search(self, requests_mock):
      newAlertReq = {
        "noticeId": "123",
        "userId": "456",
        "alertFrequency": 1,
        "alertLimitDate": "2002-12-04",
        "location": "Birmingham"
      }
      response = app.test_client().post('/api/v0/similarPets/alerts', json=newAlertReq)
      assert response.status_code == HTTPStatus.CREATED 

  @patch.multiple(
    "src.main.resources.similarPets.BackgroundScheduler", 
    get_jobs=MagicMock(return_value=[FakeScheduledJob("456","456_noticeSearch")]),
    remove_job=MagicMock(return_value=None),
    add_job=MagicMock(return_value=None),
  )
  def test_post_similar_pets_alerts_replaces_existing_jobs_for_same_user(self, requests_mock):
      newAlertReq = {
        "noticeId": "123",
        "userId": "456",
        "alertFrequency": 1,
        "alertLimitDate": "2002-12-04",
        "location": "Birmingham"
      }
      response = app.test_client().post('/api/v0/similarPets/alerts', json=newAlertReq)
      assert response.status_code == HTTPStatus.CREATED 

  @patch("src.main.resources.similarPets.BackgroundScheduler.get_jobs", side_effect=[[FakeScheduledJob("456","testScheduledJob_456")]])
  def test_post_similar_pets_alerts_deletes_alert_for_user(self, requests_mock):
      deleteAlertReq = {
        "userId": "456",
      }
      response = app.test_client().delete('/api/v0/similarPets/alerts', json=deleteAlertReq)
      assert response.status_code == HTTPStatus.CREATED 

  @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
  @patch("src.main.resources.user.requests.post", side_effect=FakePost)
  def test_search_similar_notices_and_notify_alerts_users(self, fake_get, fake_post):
      searchedNoticeId = "123"
      similarPetsAlerts = SimilarPetsAlerts()

      result = similarPetsAlerts.searchSimilarNoticesAndNotify(TEST_USERS[0]["uuid"], searchedNoticeId, 'Birmingham') 
      assert result == CLOSEST_MATCHES_RESPONSE

  @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
  @patch("src.main.resources.user.requests.post", side_effect=FakePost)
  def test_search_similar_notices_and_no_matches_found_does_not_alert_users(self, fake_get, fake_post):
      searchedNoticeId = "456"
      similarPetsAlerts = SimilarPetsAlerts()

      result = similarPetsAlerts.searchSimilarNoticesAndNotify(TEST_USERS[0]["uuid"], searchedNoticeId, 'Birmingham') 
      assert result == CLOSEST_MATCHES_EMPTY_RESPONSE   

