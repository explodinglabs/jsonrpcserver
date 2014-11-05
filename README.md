rpcserver
=========

A Flask-based JSON-RPC 2.0 server library.

Create a Flask app, and register the rpcserver blueprint to it.

    import sys, flask, rpcserver

    app = flask.Flask(__name__)
    app.register_blueprint(rpcserver.bp)

The blueprint will ensure we respond correctly with JSON-RPC every time. For
example, on 404, we respond with the JSON-RPC error, *Invalid request*.

Now create a route to handle the RPC methods:

    @app.route('/', methods=['POST'])
    def index():
        return rpcserver.dispatch(sys.modules[__name__])

The *dispatch* command will look at the method called via RPC, and call that
method in the handler which is specified in the first argument. In this case,
we've used this module as the handler.

Now write your functions that can be called via RPC:

    def add(one, two):
        return one + two

You can also use \*args or \*\*kwargs like any other python function.

Start the server:

    if __name__ == '__main__':
        app.run()
