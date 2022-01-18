import os
from typing import List
from requests import Response, post
from libs.strings import gettext   #this is called abosolute import
# from .strings import gettext   #this is called relative import

class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)  #super class allows you to give your extension a custo name



# In order to send a general email by calling send email
class Mailgun:
    #this is a way of securing our credential
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    FROM_EMAIL = 'postmaster@sandbox34d90c59e46f47fea6769287f3b64536.mailgun.org'
    FROM_TITLE = "Stores Rest API"

    @classmethod
    def send_email(
        #The email is a list of strings because we might want to send email to several users and again because we are going to import the class
        cls, email: List[str], subject: str, text: str, html: str
    ) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException(gettext("mailgun_failed_load_api_key"))

        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException(gettext("mailgun_failed_load_domain"))

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                #the above imported constant has cls because it is coming from that class
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            },
        )

        if response.status_code != 200:
            raise MailGunException(gettext("mailgun_error_send_email"))

        return response
