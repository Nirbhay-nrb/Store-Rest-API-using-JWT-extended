import os

# from datetime import timedelta
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister , User , UserLogin , TokenRefresh
from resources.item import Item , ItemList
from resources.store import StoreList , Store
from db import db

# creating app and api
app = Flask(__name__)
app.config['DEBUG'] = True
try:
    uri = os.environ.get('DATABASE_URL')
    uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
except:
    uri = 'sqlite:///data.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
# if the get method return None (that is the app is not running on heroku's computer), then the data.db on our computer will be used
# telling the app from where to find the data.db file 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # turns off the Flask_sqlalchemy tracker for changes as it cost some resources
# however this does not turn off the underlying sqlalchemy tracker
app.config['PROPAGATE_EXCEPTIONS'] = True 
# ignores the error given by flask JWT so that you can put your own personalized errors to the user
app.secret_key = 'jose' # app.config['JWT_SECRET_KEY'] -> same as app.secret_key but for JWT(feature of jwt extended)
api = Api(app)


jwt = JWTManager(app) # create the endpoint for authentication in the user resource


# claims are extra data we want to add to the payload in addition to the identity
@jwt.additional_claims_loader
def add_claims_to_loader(identity): # this parameter should be called identity only
    # this function is run when a new JWT token is created
    if identity == 1: # identity 1 means it the first user to be ever created (hard coded) , 
        # you can also get the admin ID from the database and then check
        return {'is_admin' : True}
    return {'is_admin': False}


# configuring JWT_extended
@jwt.expired_token_loader # when an access token is expired, this sends a message to the user that the token has expired
def expired_token_callback():
    return  {
        'description' : 'The token has expired',
        'error' : 'token_expired'
    } , 401

@jwt.invalid_token_loader # this function is called when the access token sent in headers is not actual JWT
def invalid_token_callback(error):
    return {
        'description' : 'Signature verification failed',
        'error' : 'invalid_token'
    } , 401

@jwt.unauthorized_loader # when there is no JWT present at all in the headers
def missing_token_callback(error):
    return {
        'description' : 'Request does not contain an access token',
        'error': 'authorization_required'
    }, 401

@jwt.needs_fresh_token_loader # when we send a refresh token(i.e. non fresh) on a fresh token endpoint, this function sends a message to the user
def token_not_fresh_callback():
    return {
        'description' : 'The token is not fresh',
        'error': 'fresh_token_required'
    }, 401

@jwt.revoked_token_loader # revoking tokens means that that token is no longer valid
# after logging out, the access token is added to the revoked tokens list so that the user cannot use that access token again
def revoked_token_callback():
    return {
        'description' : 'The token has been revoked',
        'error': 'token_revoked'
    }, 401


# adding the resource
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User , '/user/<int:user_id>')
api.add_resource(UserLogin , '/login')
api.add_resource(TokenRefresh , '/refresh')

# running the app
if __name__ == '__main__': # if in case app.py is imported then this if block won't be run
    db.init_app(app)
    if app.config['DEBUG']:
        @app.before_first_request
        def create_tables():
            db.create_all()
    app.run(port=5000) 
# as when we import a file, python actually runs the file and we dont want the app to be running again 