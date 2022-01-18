# Image are going to be saved to the file system directly  and not to the database 
# but we still want to be able to validate and schema is the appriopriate place to do this

from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage

#we are going to deserialize the data, means that the incoming data to our application which is going to be a filestorage will be analyze by this schema 
# and it's going to determine wether it is valid or not then it's going to proceed, so again the schema is going to do validation
# after is being validated we are going to use our image helper to save the image into the file system

#we then create our file storage class which is then going to inherit from the field
class FileStorageField(fields.Field):
    default_error_messages = {
        "invalid": "Not a valid image."
    }

    def _deserialize(self, value, attr, data, **kwargs) -> FileStorage: #this is the method that runs when toy do imageSchema.load, when you load it will see if it exist or not and that it is a filestorage
        if value is None:
            return None

        if not isinstance(value, FileStorage):
            self.fail("invalid")

        return value


class ImageSchema(Schema):
  # the only field we need in the image schema is an image field which is going to be filestorage field
    image = FileStorageField(required=True) # this  is a custo marsjmallow fields