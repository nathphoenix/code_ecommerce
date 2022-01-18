from ma import ma
from models.user import UserModel
from marshmallow import pre_dump  # this is a method that runs before u dump a user model into json 
# we dont want to inherit from Schema because that comes from marshmallow and it doesn't
# have enough information about the flask app that we have have linked with flask-marshmallow


class UserSchema(ma.ModelSchema):
    # this is weird in python, defining a class inside a class but you can do it with marshmallow
    # You can say a field is for loading the data and not for dumping it
    class Meta:
        model = UserModel    # this is extending the functionality of marshmallow schema and link up the user model
        load_only = ("password",)   # meaning the password field is only for loading the data, it should not be returned
        # what  is hidden from users                 # when dumping  the data
        dump_only = ("id", "confirmation")  # dump is what we want users to see

#whenever we resend the confirmation, the schema dump will eventually not include the old expired
    @pre_dump
    def _pre_dump(self, user: UserModel, **kwargs): #user is who we are about to turn into json
        user.confirmation = [user.most_recent_confirmation]
        return user















# OLD METHOD BEFORE flask_marshmallow

# from marshmallow import Schema, fields
#
#
# class UserSchema(Schema):
#     # this is weird in python, defining a class inside a class but you can do it with marshmallow
#     # You can say a field is for loading the data and not for dumping it
#     class Meta:
#         load_only = ("password",)  # meaning the password field is only for loading the data, it should not be returned
#                                    # when dumping  the data
#         dump_only = ("id",)
#         # since we have initialize our app with the flask marshmallow, what it does basically is that it get rid of
#         # duplication, since the field below has been created in our user model, it invariably becomes a duplicate here
#     id = fields.Int()
#     username = fields.Str(required=True)
#     password = fields.Str(required=True)

 