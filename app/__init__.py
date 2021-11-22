import os
import redis
from flask import Flask
from flask_cors import CORS
import pickle
import numpy as np
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
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

# tfidf
vocab = pickle.load(open('data/tfidf/vocab.pkl', 'rb'))
idf = np.load('data/tfidf/idf.npz')['idf']
tfidf = TfidfVectorizer()
tfidf.vocabulary_ = vocab
tfidf.idf_ = idf


status_code = dict(
    SUCCESS=1,
    FAILURE=0
)

from app.routes import *
from app.models import *