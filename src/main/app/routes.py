'''
from src.main.app import api

from src.main.resources.notice import Notices, UserNotices, UserNotice
from src.main.resources.pet import UserPet, UserPets, SimilarPets
from src.main.resources.user import User

# We define all the endpoints handled by this service

#api.add_resource(User, '/users')
api.add_resource(User, '/users/<string:userId>')

api.add_resource(UserPets, '/users/<string:userId>/pets')
api.add_resource(UserPet, '/users/<string:userId>/pets/<string:petId>')

api.add_resource(UserNotices, '/users/<string:userId>/notices')
api.add_resource(UserNotice, '/users/<string:userId>/notices/<string:noticeId>')

api.add_resource(Notices, '/notices')
api.add_resource(SimilarPets, '/similar-pets')
'''