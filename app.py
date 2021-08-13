from src.main import app
from flask import Flask
from flask_restful import Api
from src.main.resources.notice import Notices, UserNotices, UserNotice
from src.main.resources.pet import UserPet, UserPets, SimilarPets
from src.main.resources.user import User, Users

app = Flask(__name__)
api = Api(app, prefix='/api/v0')


# We define all the endpoints handled by this service
api.add_resource(User, '/users/<string:userId>', methods=['GET'])
api.add_resource(Users, '/users', methods=['GET', 'POST'])

api.add_resource(UserPet, '/users/<string:userId>/pets/<string:petId>')
api.add_resource(UserPets, '/users/<string:userId>/pets')

api.add_resource(UserNotice, '/users/<string:userId>/notices/<string:noticeId>')
api.add_resource(UserNotices, '/users/<string:userId>/notices')

api.add_resource(Notices, '/notices')
api.add_resource(SimilarPets, '/similar-pets')

if __name__ == '__main__':
    app.run()
