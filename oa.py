#THIS IS GOING TO HOST ALL OUR CLIENT SETTINGS
import os
from flask import g
from flask_oauthlib.client import OAuth

oauth = OAuth()   #the instance is what will be imported to our app.py

github = oauth.remote_app(
    'github',
    consumer_key=os.getenv("GITHUB_CONSUMER_KEY"),
    consumer_secret=os.getenv("GITHUB_CONSUMER_SECRET"),
    request_token_params={"scope": "user:email"}, #this will ad scope = users eail to the request
    base_url="https://api.github.com/",
    request_token_url=None,  # we set this to none because we are using OAuth 2.0
    access_token_method="POST",
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize" #where we end the user in the initial request, this takes the client id and so forth
)

@github.tokengetter
def get_github_token():
    if 'access_token' in g:
        return g.access_token