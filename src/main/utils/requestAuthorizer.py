from flask import session
from src.main.utils.jwtGenerator import JwtGenerator

class RequestAuthorizer():
    
    @classmethod
    def isRequestAuthorized(cls, request):
        try:
            authBearer = request.headers.get('Authorization')
            if not authBearer:
                return False
            (_, sessionToken) = authBearer.split(' ')
            return sessionToken in session
        except Exception as e:
            print("Error authorizing request {}".format(e))
            return False

    @classmethod
    def authenticateRequester(cls, userId, request):
        """
        Validate that the request contains an active session token,
        and authenticate the user by comparing the token's user id
        with the provided user id.
        """
        try:
            authBearer = request.headers.get('Authorization')
            if not authBearer:
                return False
            (_, sessionToken) = authBearer.split(' ')
            if not sessionToken in session:
                return False
            return JwtGenerator.decipherToken(sessionToken)['uuid'] == userId
        except Exception as e:
            print("Error authenticating user sender {}".format(e))
            return False