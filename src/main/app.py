import uuid
from flask import Flask
from flask_restful import Api

from src.main.resources.fosterVolunteerProfile import FosterVolunteerProfile, FosterVolunteerProfiles
from src.main.resources.notice import Notices, UserNotices, UserNotice, Notice
from src.main.resources.pet import UserPet, UserPets
from src.main.resources.petsFosterHistory import PetFosterHistory, PetFosterHistoryEntry
from src.main.resources.user import User, Users, UserPwd, UserPwdReset, UserContactInfo
from src.main.resources.photo import Photo, UserProfilePicture
from src.main.resources.ping import Ping
from src.main.resources.login import UserLogin, UserLogout
from src.main.resources.facebookUser import FacebookUser
from src.main.resources.similarPets import SimilarPets, SimilarPetsAlerts, SimilarPetsAlertsManual
from src.main.facebook.facebookService import FacebookPostProcessor
from src.main.resources.predictionResult import PredictionResult
from src.main.resources.emails import ConfirmationEmail, ConfirmationEmailCheck


app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
api = Api(app, prefix='/api/v0')

api.add_resource(Ping, '/', methods=['GET'])

# We define all the endpoints handled by this service
api.add_resource(User, '/users/<string:userId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(Users, '/users', methods=['GET', 'POST'])
api.add_resource(UserPwd, '/users/<string:userId>/password', methods=['PUT'])
api.add_resource(UserPwdReset, '/users/password/reset', methods=['PUT'])

api.add_resource(FacebookUser, '/users/facebook/<string:facebookId>', methods=['GET'])

api.add_resource(UserContactInfo, '/users/<string:userId>/contactInfo', methods=['GET'])

api.add_resource(UserLogin, '/users/login', methods=['POST'])
api.add_resource(UserLogout, '/users/logout', methods=['POST'])

api.add_resource(UserPet, '/users/<string:userId>/pets/<string:petId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(UserPets, '/users/<string:userId>/pets', methods=['GET', 'POST'])

api.add_resource(UserNotice, '/users/<string:userId>/notices/<string:noticeId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(UserNotices, '/users/<string:userId>/notices', methods=['GET', 'POST'])

api.add_resource(Notices, '/notices', methods=['GET'])
api.add_resource(Notice, '/notices/<string:noticeId>', methods=['GET'])
api.add_resource(SimilarPets, '/similarPets/<string:noticeId>', methods=['GET'])
api.add_resource(SimilarPetsAlerts, '/similarPets/alerts', methods=['GET', 'POST', 'DELETE'])
api.add_resource(SimilarPetsAlertsManual, '/alerts/manual', methods=['POST'])

api.add_resource(Photo, '/photos/<string:photoId>', methods=['GET'])
api.add_resource(UserProfilePicture, '/photos/profile/<string:userId>', methods=['GET'])

api.add_resource(FosterVolunteerProfile, '/fosterVolunteerProfiles/<string:profileId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(FosterVolunteerProfiles, '/fosterVolunteerProfiles', methods=['GET', 'POST'])

api.add_resource(PetFosterHistoryEntry, '/pets/<string:petId>/fosterHistory/<string:historyId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(PetFosterHistory, '/pets/<string:petId>/fosterHistory', methods=['GET', 'POST'])

api.add_resource(FacebookPostProcessor, '/facebook', methods=['GET'])

api.add_resource(ConfirmationEmail, '/emails/confirmation', methods=['POST'])
api.add_resource(ConfirmationEmailCheck, '/emails/confirmation/check', methods=['POST'])

api.add_resource(PredictionResult, '/prediction/result/failure/<string:searchedNoticeId>', methods=['POST'])
