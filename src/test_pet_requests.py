import requests
import uuid

BASE = "http://127.0.0.1:5000/api/v0/"
user_id = uuid.uuid4()

# Create pet
response1 = requests.post(BASE + f"users/{user_id}/pets", data={
    'type': 'DOG',
    'name': 'Mandi',
    'furColor': ['brown'],
    'eyesColor': ['blue', 'gray'],
    'size': 'small',
    'lifeStage': 'adult',
    'sex': 'female' ,
    'breed': 'crossbreed',
    'photos': ['pe', 't'],
    'userId': user_id
})
new_pet = response1.json()
assert response1.status_code == 201
print(new_pet)

# Get pet by userId and peyId
pet_id = response1.json()['id']
response2 = requests.get(BASE + f"users/{user_id}/pets/{pet_id}")
assert response2.status_code == 200
print(response2.json())
response3 = requests.get(BASE + f"users/{user_id}/pets/{uuid.uuid4()}")
assert response3.status_code == 404

# Get notice by userId
response21 = requests.get(BASE + f"users/{user_id}/pets")
assert response21.status_code == 200
print(response21.json())
assert len(response21.json()['pets']) == 1

response31 = requests.get(BASE + f"users/{uuid.uuid4()}/pets")
assert response31.status_code == 404

# Update pet
response4 = requests.put(BASE + f"users/{user_id}/pets/{pet_id}", data={
    '_ref': new_pet['_ref'],
    'type': 'DOG',
    'name': 'Mandi',
    'furColor': ['black'],
    'eyesColor': ['blue'],
    'size': 'medium',
    'lifeStage': 'adult',
    'sex': 'male',
    'age': 7,
    'breed': 'crossbreed' ,
    'photos': ['test'],
    'userId': user_id
})
assert response4.status_code == 200
print(response4.json())

response41 = requests.put(BASE + f"users/{user_id}/pets/{uuid.uuid4()}", data={
    '_ref': new_pet['_ref'],
    'type': 'DOG',
    'name': 'Mandi',
    'furColor': ['brown'],
    'eyesColor': ['blue'],
    'size': 'small',
    'lifeStage': 'adult',
    'sex': 'female' ,
    'breed': 'crossbreed' ,
    'photos': [''],
    'userId': user_id
})
assert response41.status_code == 404

# Delete pet
response5 = requests.delete(BASE + f"users/{user_id}/pets/{pet_id}")
assert response5.status_code == 204

response6 = requests.delete(BASE + f"users/{user_id}/pets/{uuid.uuid4()}")
assert response6.status_code == 404

