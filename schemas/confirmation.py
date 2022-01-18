from ma import ma
from models.confirmation import ConfirmationModel


class ConfirmationSchema(ma.ModelSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user",) #we don't want to dump the user information as well as user id when we dump
        dump_only = ("id", "expired_at", "confirmed") # this is what we are not going to pass to ths model 
        include_fk = True  # so that the foreign key and user_id isn't included in the dump
