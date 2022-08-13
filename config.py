import os
from dotenv import load_dotenv

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

#Import variables from env file
load_dotenv()

DB = os.getenv('DB_NAME')
USERNAME = os.getenv('USER')
PASSWORD = os.getenv('PASS')
HOST =  os.getenv('DB_HOST')


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DB}'
