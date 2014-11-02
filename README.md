rpcserver
=========

A Flask-based JSON-RPC 2.0 server.

Example
-------

    """Setup an RPC endpoint, to add two numbers"""

    import rpcserver

    class Handler:
        """RPC methods"""

        @staticmethod
        def add(num1, num2):
            """Add two numbers"""

            return num1 + num2

    app = rpcserver.Server(__name__, Handler)

    if __name__ == '__main__':
        app.run()
