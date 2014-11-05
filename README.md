jsonrpcserver
=============

A Flask-based JSON-RPC 2.0 server library.

Create a Flask app, and register the jsonrpcserver blueprint to it.

    import sys, flask, jsonrpcserver

    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

The blueprint will ensure we respond with JSON-RPC every time. For example, on
404, we respond with the error, *Invalid request*.

Now create a Flask route to handle the RPC methods:

    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

The *dispatch* command will validate the RPC request, and call the requested
method. It looks for the method in the handler which is specified in the first
argument. In this case, we've used this module as the handler.

Now write your RPC methods, as you would any other python function:

    def add(num1, num2):
        return num1 + num2

You can also use \*args or \*\*kwargs arguments.

Start the server:

    if __name__ == '__main__':
        app.run()
