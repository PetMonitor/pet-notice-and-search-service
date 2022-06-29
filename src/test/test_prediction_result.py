import json
from http import HTTPStatus

from src.main.app import app

DATABASE_URL = "http://127.0.0.1:8000"

test_client = app.test_client()

PREDICTED_NOTICES = {
    "predictedNoticeIds": [ "123e4567-e89b-12d3-a456-426614175555", "123e4567-e89b-12d3-a456-426614176666" ]
}

def test_prediction_results_failure_returns_ok(requests_mock):
    noticeId = "123e4567-e89b-12d3-a456-426614175552"
    requests_mock.post(DATABASE_URL + "/prediction/result/failure/" + noticeId, json=PREDICTED_NOTICES)

    response = test_client.post('/api/v0/prediction/result/failure/' + noticeId)
    assert response.status_code == HTTPStatus.CREATED