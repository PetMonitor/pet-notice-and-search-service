from src.main import app
from flask import Flask
from flask_restful import Api
from src.main.resources.notice import Notices, UserNotices, UserNotice
from src.main.resources.pet import UserPet, UserPets, SimilarPets
from src.main.resources.user import User, Users

app = Flask(__name__)
api = Api(app, prefix='/api/v0')


# We define all the endpoints handled by this service
api.add_resource(User, '/users/<string:userId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(Users, '/users', methods=['GET', 'POST'])

api.add_resource(UserPet, '/users/<string:userId>/pets/<string:petId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(UserPets, '/users/<string:userId>/pets', methods=['GET', 'POST'])

api.add_resource(UserNotice, '/users/<string:userId>/notices/<string:noticeId>', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(UserNotices, '/users/<string:userId>/notices', methods=['GET', 'POST'])

api.add_resource(Notices, '/notices', methods=['GET'])
api.add_resource(SimilarPets, '/similar-pets', methods=['POST'])

if __name__ == '__main__':
    app.run()
