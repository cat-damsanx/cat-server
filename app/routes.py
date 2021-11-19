from flask import request
from flask_cors import cross_origin
from app import app, question_collection
from app.utils import make_response, make_data
from catsim.catsimulator import (
    CatSimulator,
    item_bank_1PL,
    initializer,
    selector,
    estimator,
    stopper,
    get_question
)
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import base64

@app.route('/')
def index():
    return make_response(dict(data='OK bro'))


@app.route('/cat-api/estimate-ability', methods=['POST'])
@cross_origin()
def estimate_ability():
    '''
    this function is use as a part of computerized adaptive testing,
    which is estimating ability level of students
    '''
    data = request.get_json().get('data', None)
    params = dict(
        index=0,
        items=item_bank_1PL,
        administered_items=data.get('administeredItems', None),
        est_theta=data.get('currTheta', None),
        response_vector=data.get('responsePattern', None),
    )
    est_theta = estimator.estimate(**params)
    return make_response(make_data(dict(theta=est_theta)))


@app.route('/cat-api/select-question', methods=['POST'])
@cross_origin()
def select_question():
    '''
    this function is use to select the "optimal" question
    for use at that time 
    '''
    ...
    data = request.get_json().get('data', None)
    params = dict(
        index=0,
        items=item_bank_1PL,
        administered_items=data.get('administeredItems', None),
        est_theta=data.get('currTheta', None)
    )
    question_idx = selector.select(**params)
    question_code = get_question(question_idx)
    selected_question = question_collection.find({'code': question_code}, {'_id': 0})
    exam = dict(list_questions=list(selected_question))
    return make_response(make_data(
        data=dict(exam=exam, question_idx=int(question_idx))
    ))


@app.route('/cat-api/checking-stop', methods=['POST'])
@cross_origin()
def checking_stop():
    '''
    this function is use to check when a test can stop testing
    '''
    data = request.get_json().get('data', None)
    params = dict(
        index=0,
        items=item_bank_1PL,
        administered_items=data.get('administeredItems', None),
        theta=data.get('currTheta', None)
    )
    is_stop = stopper.stop(**params)
    return make_response(make_data(dict(is_stop=is_stop)))


@app.route('/cat-api/get-plot', methods=['POST'])
@cross_origin()
def get_plot():

    data = request.get_json().get('data', None)

    questionLevelPattern = np.array(data['questionLevelPattern'])
    thetaPattern = np.array(data['thetaPattern'])
    responsePattern = np.array(data['responsePattern'])

    plt.figure(figsize=(13, 7))
    x = np.arange(thetaPattern.shape[0])
    color = np.append('black', np.where(responsePattern, 'blue', 'red'))
    plt.plot(x[1:], thetaPattern[1:], label='Theta Pattern', ls='-.', color='orange', alpha=0.75)
    plt.scatter(x[:-1], questionLevelPattern, label='Item Level', marker='^')
    plt.scatter(x, thetaPattern, color=color, label='Estimated theta')
    plt.xticks(x)
    plt.xlabel('Time')
    plt.legend(loc='best')
    plt.savefig('cat.png')

    with open('cat.png', 'rb') as img:
        encoded = base64.b64encode(img.read())
        decoded = encoded.decode()

    return make_response(make_data(dict(b64Img=decoded)))