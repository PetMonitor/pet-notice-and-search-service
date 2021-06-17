import requests
import uuid

BASE = "http://127.0.0.1:5000/"
user_id = uuid.uuid4()
response = requests.get(BASE + f"users/{user_id}/reports")
print(response.json())