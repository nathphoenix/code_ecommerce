from time import time
from uuid import uuid4

from db import db

CONFIRMATION_EXPIRATION_DELTA = 1800  # tis is how long we want our confirmation link to last 30 minutes


class ConfirmationModel(db.Model):
    __tablename__ = "confirmations"

    id = db.Column(db.String(50), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel") #this is for the  relationship and is not always stored in the database
    
    #the kwargs helps us to pass in all our arguments should incase we populate our confirmation model without manually passing them in the init method
    def __init__(self, user_id: int, **kwargs):  #kwargs = expire_at, confirmed
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex  #this a string representation of a universally unique identifier version 4, it is a uniqe and randomly generated long strings
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA  # gint(time()) gives us the current time
        self.confirmed = False

    @classmethod
    def find_by_id(cls, _id: str) -> "ConfirmationModel":
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self) -> bool: #this is not doing anything but just checking if something is true or not
        return time() > self.expire_at # if the current time is greater than the set expired time which is 30 mins meaning it has expired

    def force_to_expire(self) -> None:  # forcing current confirmation to expire
        if not self.expired:   # that is why we didnt't call self.expired() as a function but just self.expired as no changes will be done
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
