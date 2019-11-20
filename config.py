import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
    SECRET_KEY = 'Super Secret'
    SEND_FILE_MAX_AGE_DEFAULT=0
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    DEBUG=True