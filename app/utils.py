from app import app, status_code
from flask import jsonify

def make_response(data={}, status=200):
    '''
        - Make a resionable response with header
        - status default is 200 mean ok
    '''
    res = jsonify(data)
    res.headers.add('Content-Type', 'application/json')
    res.headers.add('Accept', 'application/json')
    return res

def make_data(data: dict=dict(), msg: str="", status: str='SUCCESS') -> dict:
    return dict(
        data=data,
        msg=msg,
        status_code=status_code[status]
    )
