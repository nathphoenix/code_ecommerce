import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
#flask upload can be use not only for images but some other things also
from flask_uploads import configure_uploads, patch_request_class
from dotenv import load_dotenv
#This ensures the dotenv is loaded first before all our imported files 
load_dotenv(".env", verbose=True) #we have to manually load the .env file now as we have our default_config file
#which the .env file depends upon

from ma import ma 
from db import db
from oa import oauth
from blacklist import BLACKLIST
from resources.user import UserRegister, UserLogin, User, SetPassword, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.order import Order
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import Image, ImageUpload, AvatarUpload, Avatar
from libs.image_helper import IMAGE_SET
from resources.github_login import GithubLogin, GithubAuthorize

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")

 

app.config.from_object("default_config")  # load default configs from default_config.py

app.config.from_envvar(
    "APPLICATION_SETTINGS" #which is in the .env file
)  # override with config.py (APPLICATION_SETTINGS points to config.py)

patch_request_class(app, 10 * 1024 * 1024)  # restrict max upload image size to 10MB
configure_uploads(app, IMAGE_SET) # this is to link up the app with flask uploads
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):    # as except ValidationError as err
    return jsonify(err.messages), 400


jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserLogout, "/logout")

api.add_resource(Confirmation, "/user_confirm/<string:confirmation_id>")  #this is for the html page
api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/image/<string:filename>")
api.add_resource(AvatarUpload, "/upload/avatar") 
api.add_resource(Avatar, "/avatar/<int:user_id>")
api.add_resource(GithubLogin, "/login/github")
api.add_resource(GithubAuthorize, "/login/github/authorized", endpoint="github.authorize")  
api.add_resource(SetPassword, "/user/password") 
api.add_resource(Order, "/order") 

if __name__ == "__main__":
    db.init_app(app)
    # this runs in the background and it tell that marshmallow object what flask app it should be talking to
    ma.init_app(app)
    oauth.init_app(app)
    app.run(port=5000, debug=True)
