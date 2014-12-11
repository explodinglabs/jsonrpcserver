"""blueprint_test.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

import json
from flask import Flask, abort
from flask.ext.testing import TestCase
from werkzeug.http import HTTP_STATUS_CODES

from jsonrpcserver import bp, status

app = Flask(__name__)
app.register_blueprint(bp)

@app.route('/post-only', methods=['POST'])
def post_only():
    pass

@app.route('/force-error')
def force_error():
    abort(status.HTTP_500_INTERNAL_ERROR)

class TestBlueprint(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_get_method_not_allowed(self):
        response = self.client.get('/post-only')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': HTTP_STATUS_CODES[status.HTTP_405_METHOD_NOT_ALLOWED]
                },
                'id': None
            },
            json.loads(response.data.decode('utf-8'))
        )

    def test_route_not_found(self):
        response = self.client.post('/non-existant')
        self.assertEqual(status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE, response.status_code)
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_METHOD_NOT_FOUND_CODE,
                    'message': status.JSONRPC_METHOD_NOT_FOUND_TEXT,
                    'data': HTTP_STATUS_CODES[status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE]
                },
                'id': None
            },
            json.loads(response.data.decode('utf-8'))
        )

    def test_server_error(self):
        response = self.client.get('/force-error')

        self.assertEqual(status.JSONRPC_SERVER_ERROR_HTTP_CODE, response.status_code)
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_SERVER_ERROR_CODE,
                    'message': HTTP_STATUS_CODES[status.JSONRPC_SERVER_ERROR_HTTP_CODE]
                },
                'id': None
            },
            json.loads(response.data.decode('utf-8'))
        )
