from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

app = Flask(__name__)
cors = CORS(app)

client = MongoClient('mongodb://tuan.nva:data-tuan.nva@mongo.data-advising.net:27017/?authSource=QuestionDB_dev&authMechanism=SCRAM-SHA-256&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')
db = client['Service_Exam_dev']
question_collection = db['questions']

cred = credentials.Certificate('data/computerizedadaptivetesting-firebase-adminsdk-vybhu-c2b7330426.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'computerizedadaptivetesting.appspot.com'
})

bucket = storage.bucket('cat_img')

status_code = dict(
    SUCCESS=1,
    FAILURE=0
)

from app.routes import *
from app.models import *