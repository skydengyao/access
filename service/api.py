# _*_ coding: utf-8 _*_

import sys

from flask import Flask, jsonify
from control.mongodb import MongoService
from util.config import MONGODB

sys.path.append('../')

app = Flask(__name__)

api_list = {
    '/get': u'get an usable proxy',
    '/all': u'get all usable proxies',
    '/put/param': u'put an usable proxy',
}


@app.route('/')
def get():
    return jsonify(api_list)


@app.route('/get')
def mongo_get():
    db = MongoService('valid_proxy', MONGODB.get("host"), MONGODB.get("port"))
    ret = {"result": db.get(), "status": 0}
    return jsonify(ret)


@app.route('/all')
def mongo_get_all():
    db = MongoService('valid_proxy', MONGODB.get("host"), MONGODB.get("port"))
    ret = {"result": db.get_all(), "status": 0}
    return jsonify(ret)


@app.route('/put/<param>')
def mongo_put(param):
    db = MongoService('valid_proxy', MONGODB.get("host"), MONGODB.get("port"))
    try:
        db.put(param)
        ret = {"status": 0}
    except Exception as e:
        ret = {"status": 1}
    return jsonify(ret)


def run():
    app.run(host='0.0.0.0', port=8090)


if __name__ == '__main__':
    run()


