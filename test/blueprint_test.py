"""blueprint_test.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

import json
from flask import Flask, abort
from flask.ext.testing import TestCase

from jsonrpcserver import bp, status

app = Flask(__name__)
app.register_blueprint(bp)

@app.route('/force-error')
def force_error():
    abort(status.HTTP_500_INTERNAL_ERROR)

class TestBlueprint(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_client_error(self):
        response = self.client.post('/non-existant')
        self.assertEqual(404, response.status_code)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid request', 'data': 'Not Found'}, 'id': None},
            json.loads(response.data.decode('utf-8'))
        )

    def test_server_error(self):
        response = self.client.get('/force-error')

        self.assertEqual(status.HTTP_500_INTERNAL_ERROR, response.status_code)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32000, 'message': 'Server error', 'data': 'Internal Server Error'}, 'id': None},
            json.loads(response.data.decode('utf-8'))
        )
