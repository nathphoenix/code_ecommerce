import os
import re
from typing import Union
from werkzeug.datastructures import FileStorage

from flask_uploads import UploadSet, IMAGES #also allows to set an images as a constant

IMAGE_SET = UploadSet("images", IMAGES)  # set name and allowed extensions
# the string images is the name of the folder in static where the image will be save

#takes file storage and save it to a folder
def save_image(image: FileStorage, folder: str = None, name: str = None) -> str:
    return IMAGE_SET.save(image, folder, name)

#take image name and folder and return full path
#it takes in the filename without an extension and the folder which we are looking which is going to return either a string or an image or none if it can't find it
def get_path(filename: str = None, folder: str = None) -> str:
    return IMAGE_SET.path(filename, folder)

#Takes a file name and return any of the od the accepted format
def find_image_any_format(filename: str, folder: str) -> Union[str, None]:
    """
    Given a format-less filename, try to find the file by appending each of the allowed formats to the given
    filename and check if the file exists
    :param filename: formatless filename
    :param folder: the relative folder in which to search
    :return: the path of the image if exists, otherwise None
    """
    for _format in IMAGES:  # look for existing avatar and delete it
        avatar = f"{filename}.{_format}"
        avatar_path = IMAGE_SET.path(filename=avatar, folder=folder)
        if os.path.isfile(avatar_path):
            return avatar_path
    return None

# take filestorage and return the file name
def _retrieve_filename(file: Union[str, FileStorage]) -> str:
    """
    Make our filename related functions generic, able to deal with FileStorage object as well as filename str.
    """
    if isinstance(file, FileStorage):
        return file.filename
    return file

#check our regex and return whether the string matches or not
def is_filename_safe(file: Union[str, FileStorage]) -> bool:
    """
    Check if a filename is secure according to our definition
    - starts with a-z A-Z 0-9 at least one time
    - only contains a-z A-Z 0-9 and _().-
    - followed by a dot (.) and a allowed_format at the end
    """
    filename = _retrieve_filename(file)
 
    allowed_format = "|".join(IMAGES)
    #it uses the | to say the allowed format is below
    # format IMAGES into regex, eg: ('jpeg','png') --> 'jpeg|png'
    regex = f"^[a-zA-Z0-9][a-zA-Z0-9_()-\.]*\.({allowed_format})$" # the dollar sign ensures this is the end of the string we are checking
    return re.match(regex, filename) is not None #meaning the file name exist

# return full name of the image in the
#this takes the whole path and split it into two
# the two splits are the last part of the path and all the previous patrt of the part
#0 is previous part of the path, 1 is last part of the path
def get_basename(file: Union[str, FileStorage]) -> str:
    """
    Return file's basename, for example
    get_basename('some/folder/image.jpg') returns 'image.jpg'
    """
    filename = _retrieve_filename(file)
    return os.path.split(filename)[1]


def get_extension(file: Union[str, FileStorage]) -> str:
    """
    Return file's extension, for example
    get_extension('image.jpg') returns '.jpg'
    """
    filename = _retrieve_filename(file)
    return os.path.splitext(filename)[1]
