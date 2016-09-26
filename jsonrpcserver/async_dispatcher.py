"""Asynchronous dispatch"""

from .dispatcher import Requests
from .async_request import AsyncRequest
from .response import BatchResponse, NotificationResponse

class AsyncRequests(Requests): #pylint:disable=too-few-public-methods
    """Asynchronous requests"""

    def __init__(self, requests):
        super(AsyncRequests, self).__init__(requests, request_type=AsyncRequest)

    async def dispatch(self, methods):
        """Process a JSON-RPC request, calling the requested method(s)"""
        # Init may have failed to parse the request, in which case the response
        # would already be set
        if not self.response:
            # Batch request
            if isinstance(self.requests, list):
                # Batch requests - call each request, and exclude Notifications
                # from the list of responses
                self.response = BatchResponse([r.call(methods)
                                               for r in self.requests
                                               if not r.is_notification])
                # If the response list is empty, it should return nothing
                if not self.response:
                    self.response = NotificationResponse() #pylint:disable=redefined-variable-type
            # Single request
            else:
                self.response = await self.requests.call(methods)
        assert self.response, 'Response must be set'
        assert self.response.http_status, 'Must have http_status set'
        self._log_response(self.response)
        return self.response

async def dispatch(methods, requests):
    """Main public dispatch method"""
    return await AsyncRequests(requests).dispatch(methods)
