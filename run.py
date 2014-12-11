"""run.py

An example app, demonstrating how to use the library.
"""

from flask import Flask
from jsonrpcserver import bp, dispatch, exceptions


# Create a Flask app and register the blueprint.
app = Flask(__name__)
app.register_blueprint(bp)

# Add a route to pass requests on to the handling methods.
@app.route('/', methods=['POST'])
def index():
    return dispatch(MyHandlers)


# Now write the methods that carry out the requests.
class MyHandlers:

    def add(num1, num2):
        try:
            return num1 + num2
        except TypeError as e:
            raise exceptions.InvalidParams(str(e))


if __name__ == '__main__':
    app.run()
