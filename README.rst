jsonrpcserver
=============

`JSON-RPC 2.0 <http://www.jsonrpc.org/>`_ server library for Python 3.

.. sourcecode:: python

    """views.py"""

    import sys, flask, jsonrpcserver

    # Blueprint
    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

    # Route
    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

    # Handlers
    def add(num1, num2):
        return num1 + num2

    if __name__ == '__main__':
        app.run()

Test with:

    python -m views

