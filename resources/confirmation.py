from flask import render_template, make_response
from flask_restful import Resource
import traceback
from time import time

from models.confirmation import ConfirmationModel
from schemas.confirmation import ConfirmationSchema
from models.user import UserModel
# from resources.user import USER_NOT_FOUND
from libs.mailgun import MailGunException

#we are using this to handle all our error response
from libs.strings import gettext   #absolute import is very good when we have several languages,
                                  #so that we won't be importing all different kinds of languages instead of a particular language

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    # returns the confirmation page
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": gettext("confirmation_not_found")}, 404

        if confirmation.expired:
            return {"message": gettext("confirmation_link_expired")}, 400

        if confirmation.confirmed:
            return {"message": gettext("confirmation_already_confirmed")}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers,
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        """
        This endpoint is used for testing and viewing Confirmation models and should not be exposed to public.
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404
        return (
            {
              #This is only for testing for us to see the confirmation that exist in the database, so we don't have to go into the database and check for confirmtion
                "current_time": int(time()),
                # we filter the result by expiration time in descending order for convenience
                "confirmation": [
                    confirmation_schema.dump(each)
                    for each in user.confirmation.order_by(ConfirmationModel.expire_at)
                ],
            },
            200,
        )

    #THE ACTUAL RESEND CONFIRMATION
    @classmethod
    def post(cls, user_id):
        """
        This endpoint resend the confirmation email with a new confirmation model. It will force the current
        confirmation model to expire so that there is only one valid link at once.
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": gettext("user_not_found")}, 404

        try:
            # find the most current confirmation for the user
            confirmation = user.most_recent_confirmation  # using property decorator
            if confirmation: #this render old confirmation link invalid
                if confirmation.confirmed: # if the confirmation is already confirmed, return already confirmed
                    return {"message": gettext("confirmation_already_confirmed")}, 400
                confirmation.force_to_expire()  #else, force the confirmation to expire with the force_to_expire function

            new_confirmation = ConfirmationModel(user_id)  # create a new confirmation for that user_id
            new_confirmation.save_to_db()
            # Does `user` object know the new confirmation by now? Yes.
            # An excellent example where lazy='dynamic' comes into use.
            user.send_confirmation_email()  # re-send the confirmation email
            return {"message": gettext("confirmation_resend_successful")}, 201
        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message": gettext("confirmation_resend_fail")}, 500