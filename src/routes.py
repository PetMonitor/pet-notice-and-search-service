from src import api

from src.resources.notice import Notices, UserNotices, UserNotice
from src.resources.pet import UserPet, UserPets, SimilarPets

# We define all the endpoints handled by this service
api.add_resource(Notices, '/notices')
api.add_resource(UserNotices, '/users/<string:user_id>/notices')
api.add_resource(UserNotice, '/users/<string:user_id>/notices/<string:notice_id>')
api.add_resource(UserPets, '/users/<string:user_id>/pets')
api.add_resource(UserPet, '/users/<string:user_id>/pets/<string:pet_id>')
api.add_resource(SimilarPets, '/similar-pets')
