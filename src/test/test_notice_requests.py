import json
from http import HTTPStatus

from src.main.app import app
from src.main.resources.notice import UserNotice


TEST_USER = {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "_ref": "e6ebed0b-803c-43be-baaf-d370bc4e07f0",
    "username": "TerryPratchett",
    "email": "terrypratchett@discworld.com"
}

TEST_NOTICES = [
      {
        "uuid": "123e4567-e89b-12d3-a456-426614175555",
        "_ref": "447b86ea-b1c7-4e2a-a167-7542dcfbfd24",
        "petId": "123e4567-e89b-12d3-a456-426614174001",
        "userId": "123e4567-e89b-12d3-a456-426614174000",
        "noticeType": "LOST",
        "eventLocationLat": 123.0,
        "eventLocationLong": 345.0,
        "description": "My pet is lost! Please help!",
        "eventTimestamp": "2021-08-16T02:34:46+00:00",
        "street": "Green Ln",
        "neighbourhood": "Bovingdon",
        "locality": "Hertfordshire",
        "country": "England",
      },
      {
        "uuid": "123e4567-e89b-12d3-a456-426614176666",
        "_ref": "05783c09-e5bb-4a47-8978-8c61b93ca545",
        "petId": "123e4567-e89b-12d3-a456-426614174002",
        "userId": "123e4567-e89b-12d3-a456-426614175000",
        "noticeType": "FOUND",
        "eventLocationLat": 123.0,
        "eventLocationLong": 345.0,
        "description": "I found this lovely dog!",
        "eventTimestamp": "2021-08-16T02:34:46+00:00",
        "street": "Green Ln",
        "neighbourhood": "Bovingdon",
        "locality": "Hertfordshire",
        "country": "England",
      }
]

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


RESPONSE_BODY_IDX = 0
RESPONSE_STATUS_IDX = 1

DATABASE_URL = "http://127.0.0.1:8000"
DATABASE_USER_NOTICES_URL = DATABASE_URL + "/users/" + TEST_USER["uuid"] + "/notices"


def test_get_notices_returns_all_notices(requests_mock):
    requests_mock.get(DATABASE_URL + "/notices", json=TEST_NOTICES)
    c = app.test_client()
    response = c.get('/api/v0/notices')
    responseBody = response.json

    # Verify response content
    assert len(responseBody) == len(TEST_NOTICES)
    for i in range(len(TEST_NOTICES)):
        assert json.dumps(responseBody[i], sort_keys=True) == json.dumps(TEST_NOTICES_OUTPUT[i], sort_keys=True)
    assert response.status_code == HTTPStatus.OK


def test_get_notice_by_id_returns_requested_notice(requests_mock):
    noticeId = TEST_NOTICES[0]["uuid"]
    requests_mock.get(DATABASE_USER_NOTICES_URL + "/" + noticeId, json=TEST_NOTICES[0])
    response = UserNotice().get(TEST_USER["uuid"], noticeId)
    notice = response[RESPONSE_BODY_IDX]

    # Verify response content 
    assert len(notice) == len(TEST_NOTICES_OUTPUT[0])
    assert json.dumps(notice, sort_keys=True) == json.dumps(TEST_NOTICES_OUTPUT[0], sort_keys=True)
    assert response[RESPONSE_STATUS_IDX] == HTTPStatus.OK

