from flask_restful import Resource

class Ping(Resource):

    def get(self):
        return { "res": "Age shall not wither her, nor custom stale her infinite variety." }