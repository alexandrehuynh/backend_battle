from flask import Flask, Blueprint, jsonify, send_file
from flask_migrate import Migrate 
from flask_cors import CORS
from flask_jwt_extended import JWTManager 
import uuid
import os
import firebase_admin
from firebase_admin import credentials



# internal imports
from config import Config 
from .models import login_manager, db, Pokemon
from .api.routes import api


#instantiate our Flask app
app = Flask(__name__) #is passing in the name of our directory as the name of our app
cors = CORS(app) #Cross Origin Resource Sharing aka allowing other apps to talk to our API

#going to tell our app what Class to look to for configuration
app.config.from_object(Config)
jwt = JWTManager(app) # allows our app to use JWTMaanager from anywhere 


@app.route('/')
def index():
    return send_file('./static/images/enterthegate.jpeg', mimetype='image/jpeg')


app.register_blueprint(api)

# wrap our whole app in our login_manager so we can use it wherever in our app
login_manager.init_app(app)
login_manager.login_view = 'auth.sign_id' #authentication route 
login_manager.login_message = 'Hey you! Login Please' 
login_manager.login_message_category = 'warning'

# intantiate our database & wrap our app in it
db.init_app(app)
migrate = Migrate(app, db) #things we are connecting/migrating (our application to our database)
# app.json_encoder = JSONEncoder # we are not instantiating this but rather point to this class 

# Access the environment variable
sdk_path = os.getenv('FIREBASE_CREDENTIALS')
if not sdk_path:
    raise ValueError('The FIREBASE_CREDENTIALS environment variable is not set.')

# Initialize Firebase Admin SDK
cred = credentials.Certificate(sdk_path)
firebase_admin.initialize_app(cred)