from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import send_file, request # we use it to access the file that was sent 
#the send_file allows you to send a binary file like an image instead of json
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import os  #this will be necessary to delete image

from libs import image_helper
from libs.strings import gettext
from schemas.image import ImageSchema

image_schema = ImageSchema()

#we change to classmethod since we are not using self for anything

class ImageUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        """
        This endpoint is used to upload an image file. It uses the
        JWT to retrieve user information and save the image in the user's folder.
        If a file with the same name exists in the user's folder, name conflicts
        will be automatically resolved by appending a underscore and a smallest
        unused integer. (eg. filename.png to filename_1.png).
        """
        data = image_schema.load(request.files) # request.file is a dictionary inside request that has the key of file name to the data of the file,
                                                #the data is going to be a file storage object from werkzeug, bcos werkzeug is going to take all the incoming files and is going to wrap them with this filestorage object fo our benefit
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            # save(self, storage, folder=None, name=None)
            image_path = image_helper.save_image(data["image"], folder=folder) #here we get the whole image path
            # here we only return the basename of the image and hide the internal folder structure from our user
            basename = image_helper.get_basename(image_path)
            return {"message": gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:  # forbidden file type
            extension = image_helper.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400


class Image(Resource):
    @classmethod
    @jwt_required    # if you are logged in
    def get(cls, filename: str):  #we look at the image folder for the image, with different folder for different users
        """
        This endpoint returns the requested image if exists. It will use JWT to
        retrieve user information and look for the image inside the user's folder.
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"  # check if we are able to get the image
        # check if filename is URL secure
        if not image_helper.is_filename_safe(filename): #we want to check if the file we are looking for is safe 
            return {"message": gettext("image_illegal_file_name").format(filename)}, 400
        try:
            # try to send the requested file to the user with status code 200
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404

    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        """
        This endpoint is used to delete the requested image under the user's folder.
        It uses the JWT to retrieve user information.
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        # check if filename is URL secure
        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("image_illegal_file_name").format(filename)}, 400

        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"message": gettext("image_deleted").format(filename)}, 200
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404
        except:
            traceback.print_exc()
            return {"message": gettext("image_delete_failed")}, 500


class AvatarUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        """
        This endpoint is used to upload user avatar. All avatars are named after the user's id
        in such format: user_{id}.{ext}.
        It will overwrite the existing avatar.
        """
        data = image_schema.load(request.files) #we are validating that the file we recieve is a valid file
        filename = f"user_{get_jwt_identity()}"  #the filename is something we are goung to overwrite
        folder = "avatars"  #foldername is avatar
        avatar_path = image_helper.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": gettext("avatar_delete_failed")}, 500

        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext  # use our naming format + true extension
            avatar_path = image_helper.save_image(
                data["image"], folder=folder, name=avatar
            )
            basename = image_helper.get_basename(avatar_path)
            return {"message": gettext("avatar_uploaded").format(basename)}, 200
        except UploadNotAllowed:  # forbidden file type
            extension = image_helper.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400


class Avatar(Resource):
    @classmethod
    def get(cls, user_id: int):
        """
        This endpoint returns the avatar of the user specified by user_id.
        """
        folder = "avatars"
        filename = f"user_{user_id}"
        avatar = image_helper.find_image_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        return {"message": gettext("avatar_not_found")}, 404
