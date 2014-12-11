"""run.py

An example app, demonstrating how to use the library.
"""

import sys
import logging

from flask import Flask
from jsonrpcserver import dispatch, bp

# Create flask app
app = Flask(__name__)
app.testing = True

# Blueprint
app.register_blueprint(bp)

# Route
@app.route('/', methods=['POST'])
def index():
    return dispatch(sys.modules[__name__])

# Handler
def add(one, two):
    return one + two

if __name__ == __main__:
    app.run()
