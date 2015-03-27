"""test_blueprint.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods,no-init

from unittest import main

from flask import Flask, abort, Response
from flask.ext.testing import TestCase #pylint:disable=no-name-in-module,import-error
from werkzeug.http import HTTP_STATUS_CODES

from jsonrpcserver import blueprint, bp, status
from jsonrpcserver.exceptions import InvalidParams


app = Flask(__name__)
app.register_blueprint(bp)


@app.route('/post-only', methods=['POST'])
def post_only():
    return Response('ok')


@app.route('/force-error', methods=['POST'])
def force_error():
    abort(status.HTTP_500_INTERNAL_ERROR)


class TestBlueprint(TestCase):

    @staticmethod
    def create_app():
        app.config['TESTING'] = True
        return app

    def test_ok(self):
        response = self.client.post('/post-only')
        self.assert200(response)

    def test_wrong_http_method(self):
        # Using GET instead of POST
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

    @staticmethod
    def test_custom_exception_error_handler():
        blueprint.custom_exception_error_handler(InvalidParams('Test'))

if __name__ == '__main__':
    main()
