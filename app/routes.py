from flask import request
from flask_cors import cross_origin
from app import app, question_collection, redis_client
from app.utils import make_response, make_data, get_exam
from catsim.catsimulator import (
    CatSimulator,
    item_bank_1PL,
    initializer,
    selector,
    estimator,
    stopper,
    get_question,
    cb_groups,
    cb_names,
    cb_props
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
    need config with session id
    '''
    ...
    data = request.get_json().get('data', None)
    exam_id = data.get('examId', None)

    administered_items = data.get('administeredItems', [])
    response_pattern = data.get('responsePattern', [])

    # if len(response_pattern) > len(administered_items):
    #     question_code = get_question(administered_items[-1])
    #     exam = get_exam(question_code)
    #     return make_response(make_data(
    #         data=dict(exam=exam, question_idx=int(question_idx))
    #     ))

    params = dict(
        index=0,
        items=item_bank_1PL,
        administered_items=data.get('administeredItems', None),
        est_theta=data.get('currTheta', None),
        exam_id=exam_id,
        cb_groups=cb_groups,
        cb_names=cb_names,
        cb_props=cb_props
    )
    question_idx = selector.select(**params)

    # update content balancing data of an exam
    category = cb_groups[question_idx] # lấy category tương ứng
    old_category_value = float(redis_client.hget(exam_id, category))
    redis_client.hmset(exam_id, {category: old_category_value + 1}) # cộng thêm 1 vào

    question_code = get_question(question_idx)
    exam = get_exam(question_code)
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

    # case where stop is satisfied
    # if is_stop:
    # redis_client.delete(data.get('examId', None))

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
    plt.plot(x[1:], thetaPattern[1:], label='Theta Pattern',
             ls='-.', color='orange', alpha=0.75)
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


@app.route('/cat-api/get-exam-id', methods=['GET'])
def get_exam_id():
    '''
    get exam id based on size of redis 
    and add all category to that
    '''
    exam_id = redis_client.dbsize()
    mapping = dict(zip(cb_names, np.zeros_like(cb_names)))
    redis_client.hmset(exam_id, mapping)
    return make_response(make_data(dict(exam_id=exam_id), msg="Get exam id successfully!"))


# @app.route('/testing')
# def testing():
#     redis_client.set('hai', 2)
#     redis_client.hmset('session1', dict(chapter1=0.5, chapter2=0.9))
#     return make_response(make_data(msg="This is just test"))
