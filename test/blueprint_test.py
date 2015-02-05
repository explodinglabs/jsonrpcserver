"""blueprint_test.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

import json
from flask import Flask, abort
from flask.ext.testing import TestCase #pylint:disable=no-name-in-module,import-error
from werkzeug.http import HTTP_STATUS_CODES

from jsonrpcserver import bp, status

app = Flask(__name__)
app.register_blueprint(bp)

@app.route('/post-only', methods=['POST'])
def post_only():
    pass

@app.route('/force-error', methods=['POST'])
def force_error():
    abort(status.HTTP_500_INTERNAL_ERROR)

class TestBlueprint(TestCase):
    #pylint:disable=no-init

    def create_app(self): #pylint:disable=no-self-use
        app.config['TESTING'] = True
        return app

    def test_wrong_http_method(self):
        """Use GET instead of POST"""
        response = self.client.get('/post-only')
        self.assert405(response)
        self.assertIn(('Content-Type', 'text/html'), list(response.headers))

    def test_client_html(self):
        response = self.client.post('/non-existant')
        self.assert404(response)
        self.assertIn(('Content-Type', 'text/html'), list(response.headers))

    def test_client_json(self):
        response = self.client.get('/non-existant', headers={'Accept': 'application/json-rpc'})
        self.assert404(response)
        self.assertIn(('Content-Type', 'application/json'), list(response.headers))
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': HTTP_STATUS_CODES[status.HTTP_404_NOT_FOUND]
                },
                'id': None
            },
            response.json
        )

    def test_server_html(self):
        response = self.client.post('/force-error')
        self.assert500(response)
        self.assertIn(('Content-Type', 'text/html'), list(response.headers))

    def test_server_json(self):
        response = self.client.post('/force-error', headers={'Accept': 'application/json'})
        self.assert500(response)
        self.assertIn(('Content-Type', 'application/json'), list(response.headers))
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_SERVER_ERROR_CODE,
                    'message': HTTP_STATUS_CODES[status.JSONRPC_SERVER_ERROR_HTTP_CODE]
                },
                'id': None
            },
            response.json
        )
