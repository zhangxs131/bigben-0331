#!/usr/bin/env python

import handler
from flask import Flask, request
from waitress import serve

from common import set_log

app = Flask(__name__)
set_log()


class Event:
    def __init__(self):
        self.body = request.get_data()
        self.headers = request.headers
        self.method = request.method
        self.query = request.args
        self.path = request.path


@app.route('/_/health', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def health():
    return "ok"


@app.route('/-/reloaddata', methods=['GET', 'POST'])
def call_reloader():
    event = Event()
    return handler.reload_models(event)


@app.route('/', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def call_handler(path):
    event = Event()
    return handler.handle(event)


if __name__ == '__main__':
    handler.init()
    serve(app, host='0.0.0.0', port=8080, connection_limit=1000, threads=8)
