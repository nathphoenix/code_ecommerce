from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
    fresh_jwt_required,
)
import traceback
from marshmallow import ValidationError
from schemas.user import UserSchema
from models.user import UserModel
from models.confirmation import ConfirmationModel
from blacklist import BLACKLIST
from libs.mailgun import MailGunException
from libs.strings import gettext

# we are no longer using this again because of marshmallows

# _user_parser = reqparse.RequestParser()
# _user_parser.add_argument(
#     "username", type=str, required=True, help=BLANK_ERROR.format("username")
# )
# _user_parser.add_argument(
#     "password", type=str, required=True, help=BLANK_ERROR.format("password")
# )

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        # try:

        user = user_schema.load(request.get_json())
        print(user)
        # data = _user_parser.parse_args()
        # except ValidationError as err:
        #     return err.messages, 400
        if UserModel.find_by_username(user.username):
            return {"message": gettext("user_username_exists")}, 400

        #in order to enaure that our email is unique
        if UserModel.find_by_email(user.email):
            return {"message": gettext("user_email_exists")}, 400

        try:
            # user = UserModel(**user)  # we no longer need to create a user model down here
            user.save_to_db()
            confirmation = ConfirmationModel(user.id) # we want to create a confirmation model with the user then save to database before sending confirmation email
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": gettext("user_registered")}, 201
        
        except MailGunException as e:
            user.delete_from_db()  # so that if registration is incomplete without email, we want to remove the user as they can't confirm their account
            return{"message": str(e)}, 500
        except: #failed to save user to db by deleting the entered data
            traceback.print_exc()
            user.delete_from_db()
            return{"message": gettext("user_error_creating")}, 500


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404
        return user_schema.dump(user), 200
    # since we are using marshmallow now, we are no longer responding with user.json() which is required by reqparse
    # instead we are using the deserialize form by using dump

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404
        user.delete_from_db()
        return {"message":gettext("user_deleted")}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):

        user_json = request.get_json()
        user_data = user_schema.load(user_json, partial=("email",))  # we ignore the email field if it is not present
        # we have to tell marshmallow to forget about specific field like the

        user = UserModel.find_by_username(user_data.username)

        # this is what the `authenticate()` function did in security.py
        if user and user.password and safe_str_cmp(user.password, user_data.password):
            confirmation = user.most_recent_confirmation  #this is ok as we expire old confirmation and pick the latest confirmation
            if confirmation and confirmation.confirmed: #we check if user is activated or not after logging in
                # identity= is what the identity() function did in security.py—now stored in the JWT
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            else:
                return {"message": gettext("user_not_confirmed").format(user.email)}, 400
        return {"message": gettext("user_invalid_credentials")}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": gettext("user_logged_out").format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
 

class SetPassword(Resource):
    @classmethod
    @fresh_jwt_required
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)
        user = UserModel.find_by_username(user_data.username)

        if not user:
            return {"message": gettext("user_not_found")}, 400

        user.password = user_data.password
        user.save_to_db()

        return {"message": gettext("user_password_updated")}, 201

# class UserConfirm(Resource):
#     @classmethod
#     def get(cls, user_id: int):
#         user = UserModel.find_by_id(user_id)
#         if not user:
#             return {"message": USER_NOT_FOUND}
#         else:
#             user.activated = True
#             user.save_to_db()

#             # return redirect("http://localhost:300", code=302)  # should in case we want to redirect our users
#             headers = {"Content-Type": "text/html"}  # tells the browser that the content it's getting is an HTML page
#             # if not, by default flask will tell the browser that the content they are getting is JSON
#             return make_response(
#                 render_template("confirmation_page.html", email=user.username), 200, headers)