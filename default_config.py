import os

#this is what our application uses by default, tha is why debug is set to true to understands all errors

DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True # this is also necessary for error_handler below by allowing extensions to propagte our app
UPLOADED_IMAGES_DEST = os.path.join("static", "images")  # manage image root folder
#this is only set for cookies
SECRET_KEY= os.environ.get("APP_SECRET_KEY")  # could do app.config['JWT_SECRET_KEY'] if we prefer, will crash if user set up our app without it in this format
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = [
    "access",
    "refresh",
]  # allow blacklisting for access and refresh tokens
