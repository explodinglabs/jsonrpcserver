"""Asynchronous dispatch"""
import asyncio

from . import config
from .async_request import AsyncRequest
from .dispatcher import Requests
from .response import BatchResponse, NotificationResponse


class AsyncRequests(Requests):
    """Asynchronous requests."""
    def __init__(self, requests, request_type=AsyncRequest):
        super(AsyncRequests, self).__init__(requests, request_type=request_type)

    async def dispatch(self, methods, context=None):
        """
        Process a JSON-RPC request.

        Calls the requested method(s), and returns the result.
        """
        # Init may have failed to parse the request, in which case the response
        # would already be set
        if not self.response:
            # Batch request
            if isinstance(self.requests, list):
                # First convert each to a Request object
                requests = [self.request_type(r, context=context) for r in self.requests]
                # Call each request
                response = await asyncio.gather(*[r.call(methods) for r in requests])
                # Remove notification responses (as per spec)
                response = [r for r in response if not r.is_notification]
                # If the response list is empty, return nothing
                self.response = BatchResponse(response) if response else NotificationResponse()
            # Single request
            else:
                # Convert to a Request object
                request = self.request_type(self.requests, context=context)
                # Call the request
                self.response = await request.call(methods)
        assert self.response, 'Response must be set'
        assert self.response.http_status, 'Must have http_status set'
        if config.log_responses:
            self._log_response(self.response)
        return self.response


async def dispatch(methods, requests, context=None):
    """Main public dispatch method."""
    return await AsyncRequests(requests).dispatch(methods, context=context)
