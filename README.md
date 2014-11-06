jsonrpcserver
=============

A [JSON-RPC 2.0](http://www.jsonrpc.org/) server library for Python 3.

    import sys, flask, jsonrpcserver

    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

    def add(num1, num2):
        return num1 + num2

    if __name__ == '__main__':
        app.run()

What's going on here? First we create a Flask app, and register the
jsonrpcserver blueprint to it.

    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

The blueprint will ensure we respond with JSON-RPC every time. For example, on
404, we respond with the 404 status code along with the JSON-RPC error, *Invalid
request*.

Now create a route to handle the RPC methods:

    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

The ``dispatch`` call will validate the RPC request, and call the requested
*method*. We pass the current module to it, as the handler of the methods.

Now write the RPC handling methods, as you would any other Python function:

    def add(num1, num2):
        return num1 + num2

The RPC handling functions can receive any combination of positional, positional
expansion or keyword expansion arguments.

    def find(name, *args, **kwargs):
        pass

Exceptions
----------

If the arguments received are no good, raise the ``InvalidParams`` exception:

    def add(num1, num2='Not a number'):
        try:
            return num1 + num2
        except TypeError:
            raise jsonrpcserver.exceptions.InvalidParams()

If you need a client, try my
[jsonrpcclient](https://bitbucket.org/beau-barker/jsonrpcclient) library.
