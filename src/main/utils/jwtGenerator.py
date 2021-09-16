import jwt

class JwtGenerator():

    ALGORITHM = "HS256"
    SECRET_KEY = "666"

    @classmethod
    def generateToken(cls, userData):
        token = jwt.encode(userData, JwtGenerator.SECRET_KEY, algorithm=JwtGenerator.ALGORITHM)
        return token

    @classmethod
    def decipherToken(cls, encodedJwtToken):
        return jwt.decode(encodedJwtToken, JwtGenerator.SECRET_KEY, algorithms=[JwtGenerator.ALGORITHM])
