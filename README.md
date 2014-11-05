jsonrpcserver
=============

A Flask-based JSON-RPC 2.0 server library.

Create a Flask app, and register the jsonrpcserver blueprint to it.

    import sys, flask, jsonrpcserver

    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

The blueprint will ensure we respond with JSON-RPC every time. For example, on
404, we respond with the JSON-RPC error, *Invalid request*.

Now create a route to handle the RPC methods:

    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

The ``dispatch`` command will validate the RPC request, and call the requested
*method*. We pass the current module to it, as the handler of the methods.

Now write your RPC methods, as you would any other python function:

    def add(num1, num2):
        return num1 + num2

You can even receive positional or keyword arguments.

    def find(name, *args, **kwargs):
        pass

If there's a problem with the arguments, you should raise the ``InvalidParams``
exception:

    def add(num1, num2='Not a number'):
        try:
            return num1 + num2
        except:
            raise jsonrpcserver.exceptions.InvalidParams()

If you need a client library, try my
[jsonrpcclient](https://bitbucket.org/beau-barker/jsonrpcclient).
