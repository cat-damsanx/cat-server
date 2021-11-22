import os
import redis
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import storage

app = Flask(__name__)
cors = CORS(app)
redis_client = redis.from_url(os.environ['REDIS_URL'])

client = MongoClient(os.environ['MONGO_URI'].replace('"', ''))
db = client['Service_Exam_dev']
question_collection = db['questions']

# cred = credentials.Certificate('data/computerizedadaptivetesting-firebase-adminsdk-vybhu-c2b7330426.json')
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'computerizedadaptivetesting.appspot.com'
# })

# bucket = storage.bucket('cat_img')

status_code = dict(
    SUCCESS=1,
    FAILURE=0
)

from app.routes import *
from app.models import *