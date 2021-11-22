import numpy as np
from flask import jsonify
from app import app, status_code, redis_client, question_collection


def make_response(data={}, status=200):
    '''
        - Make a resionable response with header
        - status default is 200 mean ok
    '''
    res = jsonify(data)
    res.headers.add('Content-Type', 'application/json')
    res.headers.add('Accept', 'application/json')
    return res


def make_data(data: dict = dict(), msg: str = "", status: str = 'SUCCESS') -> dict:
    return dict(
        data=data,
        msg=msg,
        status_code=status_code[status]
    )


def get_exam(question_code) -> dict:
    '''
    trả về exam của một câu hỏi
    '''
    selected_question = question_collection.find(
        {'code': question_code}, {'_id': 0})
    exam = dict(list_questions=list(selected_question))
    return exam


def get_cb_data(exam_id: int) -> dict:
    '''
    get content balancing data of a specific exam_id
    '''
    data = redis_client.hgetall(exam_id)
    data = {k.decode('utf-8'): float(v) for k, v in data.items()}
    return data


def update_cb_data(cb_dictionary: dict, cb_names: np.ndarray, cb_props: np.ndarray) -> dict:
    cb_dictionary
