import os

# from datetime import timedelta
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister , User , UserLogin
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


# adding the resource
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User , '/user/<int:user_id>')
api.add_resource(UserLogin , '/login')

# running the app
if __name__ == '__main__': # if in case app.py is imported then this if block won't be run
    db.init_app(app)
    if app.config['DEBUG']:
        @app.before_first_request
        def create_tables():
            db.create_all()
    app.run(port=5000) 
# as when we import a file, python actually runs the file and we dont want the app to be running again 