# Temporal dictionary to hold values until we make the requests to the database service
USER_ID1 = uuid.uuid4()
NOTICE_ID1 = uuid.uuid4()
USER_ID2 = uuid.uuid4()
NOTICE_ID2 = uuid.uuid4()
USER_ID3 = uuid.uuid4()
NOTICE_ID3 = uuid.uuid4()
notices_db = {
    str(USER_ID1): {
        str(NOTICE_ID1): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'noticeType': NoticeType.FOUND.name,
            'eventLocation': "CABA",
            'description': "insert text",
            'eventTimestamp': datetime.now(timezone.utc).timestamp(),
            'userId': USER_ID1,
            'petId': uuid.uuid4()
        }
    },
    str(USER_ID2): {
        str(NOTICE_ID2): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'noticeType': NoticeType.LOST.name,
            'eventLocation': "Rosario",
            'description': "insert text",
            'eventTimestamp': datetime.now(timezone.utc).timestamp(),
            'userId': USER_ID2,
            'petId': uuid.uuid4()
        }
    },
    str(USER_ID3): {
        str(NOTICE_ID3): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'noticeType': NoticeType.FOR_ADOPTION.name,
            'eventLocation': "Campana",
            'description': "insert text",
            'eventTimestamp': datetime.now(timezone.utc).timestamp(),
            'userId': USER_ID3,
            'petId': uuid.uuid4()
        }
    }
}

# Temporal dictionary to hold values until we make the requests to the database service
PET_ID1 = uuid.uuid4()
PET_ID2 = uuid.uuid4()
PET_ID3 = uuid.uuid4()
pets_db = {
    str(USER_ID1): {
        str(PET_ID1): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'type': PetType.DOG.name,
            'name': "firulais",
            'furColor': ['brown'],
            'eyesColor': ['black'],
            'size': PetSize.SMALL.name,
            'lifeStage': PetLifeStage.ADULT.name,
            'age': 8,
            'sex': PetSex.MALE.name,
            'breed': 'crossbreed',
            'description': 'some description',
            'photos': ['test'],
            'userId': USER_ID1
        }
    },
    str(USER_ID2): {
        str(PET_ID2): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'type': PetType.DOG.name,
            'name': "blondie",
            'furColor': ['blonde'],
            'eyesColor': ['blue', 'gray'],
            'size': PetSize.MEDIUM.name,
            'lifeStage': PetLifeStage.BABY.name,
            'age': None,
            'sex': PetSex.FEMALE.name,
            'breed': 'crossbreed',
            'description': 'some description',
            'photos': ['test'],
            'userId': USER_ID2
        }
    },
    str(USER_ID3): {
        str(PET_ID3): {
            'id': uuid.uuid4(),
            '_ref': uuid.uuid4(),
            'type': PetType.CAT.name,
            'name': "yuli",
            'furColor': ['white', 'orange'],
            'eyesColor': ['brown'],
            'size': PetSize.SMALL.name,
            'lifeStage': PetLifeStage.ADULT.name,
            'age': 6,
            'sex': PetSex.FEMALE.name,
            'breed': 'crossbreed',
            'description': 'some description',
            'photos': ['test'],
            'userId': USER_ID3
        }
    }
}