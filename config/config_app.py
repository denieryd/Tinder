import os

DEBUG = False

SERVICE_TOKEN = 'cc527c5bcc527c5bcc527c5b57cc3b59f3ccc52cc527c5b90d386a404a621db52df7451'
SECURE_KEY = 'TEfi1tDvNBxTQgk4eMI1'
APP_ID = '6890920'

OAUTH_LINK = 'https://oauth.vk.com/authorize?client_id=549005' \
             '7&display=page&redirect_uri=https://oauth.vk.co' \
             'm/blank.html&scope=friends,photos,groups,pages&response_type=token&v=5.52'

DB_NAME = 'tinderdb'
DB_USER = 'tinderuser'

PATH_TO_OUTPUT_RESULT = 'output.json'
PATH_TO_DATA_FOR_TEST = os.path.join('tests', 'data_for_test.txt')
ROOT_OF_PROJECT = os.path.join(os.path.dirname(os.path.abspath(os.pardir)), 'tinder')

STANDARD_SEARCH_OFFSET = 30

VERSION_VK_API = 5.92

POINT_OF_GROUP_UNIT = 0.05
POINT_OF_FRIEND_UNIT = 0.1
POINT_OF_AGE = 2.5
POINT_OF_MUSIC = 2.0
POINT_OF_BOOKS = 0.8
