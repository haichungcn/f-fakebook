import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SEND_FILE_MAX_AGE_DEFAULT=0
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    EMAIL_API = os.environ.get('EMAIL_API')

    DEBUG=True