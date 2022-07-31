from flask_restful import Resource, reqparse
from models.user import UserModel
from flask_jwt_extended import create_access_token, create_refresh_token

_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    'username',
    type = str,
    required=True,
    help = 'This field cannot be blank'
)
_user_parser.add_argument(
    'password',
    type = str,
    required=True,
    help = 'This field cannot be blank'
)

class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        # checking if user already exists or not
        if UserModel.find_by_username(data['username']) is not None:
            # user exists
            return {'message' : 'A user with that user name already exists'} , 400 # for bad request

        # user does not exist
        user = UserModel(data['username'] , data['password'])
        user.save_to_db()
        return {'message' : 'User created succesfully'} , 201 # 201 for created

class User(Resource):
    @classmethod
    def get(cls , user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message' : 'User not found'} , 404
        return user.json() 

    def delete(cls , user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message' : 'User not found'} , 404
        user.delete_from_db()
        return {'message' : 'User deleted'}

class UserLogin(Resource):

    def post(self):
        # get data from _user_parser
        data = _user_parser.parse_args()

        # find user in database
        user = UserModel.find_by_username(data['username'])

        # check password
        if user and user.password == data['password'] : 
            # create access token
            access_token = create_access_token(identity = user.id , fresh = True)
            # create refresh token
            refresh_token = create_refresh_token(user.id)
            # return them
            return {
                'access_token' : access_token,
                'refresh_token' : refresh_token
            }
        
        # user doesnt exist or password is wrong
        return {'message' : 'Invalid Credentials'}, 401 # means unauthorized
