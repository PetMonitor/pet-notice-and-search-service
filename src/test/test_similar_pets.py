
import json
from http import HTTPStatus
from mock import patch, MagicMock

from src.main.app import app
from src.main.resources.similarPets import SimilarPetsAlerts

DATABASE_URL = "http://127.0.0.1:8000"
DATABASE_SIMILAR_PETS_URL = DATABASE_URL + "/similarPets" 

CLOSEST_MATCHES_RESPONSE = {
    "closestMatches": [ "123e4567-e89b-12d3-a456-426614175555", "123e4567-e89b-12d3-a456-426614176666" ]
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



test_client = app.test_client()

def test_get_similar_pets_returns_list_with_similar_notices(requests_mock):
    searchedNoticeId = "123e4567-e89b-12d3-a456-426614175552"
    requests_mock.get(DATABASE_URL + "/pets/finder/" + searchedNoticeId, json=CLOSEST_MATCHES_RESPONSE)
    requests_mock.get(DATABASE_URL + "/notices/" + CLOSEST_MATCHES_RESPONSE["closestMatches"][0], json=TEST_NOTICES_OUTPUT[0])
    requests_mock.get(DATABASE_URL + "/notices/" + CLOSEST_MATCHES_RESPONSE["closestMatches"][1], json=TEST_NOTICES_OUTPUT[1])

    response = test_client.get('/api/v0/similarPets/' + searchedNoticeId)
    assert response.status_code == HTTPStatus.OK

@patch("src.main.resources.similarPets.BackgroundScheduler.get_jobs", side_effect=[TEST_SCHEDULED_JOBS])
def test_get_similar_pets_alerts_returns_list_of_all_scheduled_alerts(requests_mock):
    response = test_client.get('/api/v0/similarPets/alerts')
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
def test_post_similar_pets_alerts_schedules_programmed_search(requests_mock):
    newAlertReq = {
      "noticeId": "123",
      "userId": "456",
      "alertFrequency": 1,
      "alertLimitDate": "2002-12-04"
    }
    response = test_client.post('/api/v0/similarPets/alerts', json=newAlertReq)
    assert response.status_code == HTTPStatus.CREATED 

@patch.multiple(
  "src.main.resources.similarPets.BackgroundScheduler", 
  get_jobs=MagicMock(return_value=[FakeScheduledJob("456","456_noticeSearch")]),
  remove_job=MagicMock(return_value=None),
  add_job=MagicMock(return_value=None),
)
def test_post_similar_pets_alerts_replaces_existing_jobs_for_same_user(requests_mock):
    newAlertReq = {
      "noticeId": "123",
      "userId": "456",
      "alertFrequency": 1,
      "alertLimitDate": "2002-12-04"
    }
    response = test_client.post('/api/v0/similarPets/alerts', json=newAlertReq)
    assert response.status_code == HTTPStatus.CREATED 