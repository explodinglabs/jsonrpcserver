"""__init__.py"""

from logging import getLogger, StreamHandler

request_log = getLogger('jsonrpcserver.request')
response_log = getLogger('jsonrpcserver.response')

from jsonrpcserver.dispatcher import Dispatcher
