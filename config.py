import os
#this is one is particularly for production environment
#it will override settings from the default_config and set them to our final configuration
# when our app is shared with users
# will also set our default dabase to postgres on the production environment instead of sqlite



DEBUG = False
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data.db")
# the two url are there incase we don'r want to use sqlite, and if the  database_uri is
# empty then sqlite will be use by defualt