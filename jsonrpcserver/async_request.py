"""Asynchronous request."""
from .request import Request
from .request_utils import *
from .response import Response, RequestResponse, NotificationResponse


class AsyncRequest(Request):
    """Asynchronous request"""

    async def call(self, methods):
        # Validation or parsing may have failed in __init__, in which case
        # there's no point calling. It would've already set the response.
        if not self.response:
            # Handles setting the result/exception of the call
            with self.handle_exceptions():
                # Get the method object from a list (raises MethodNotFound)
                callable_ = self._get_method(methods)
                # Ensure the arguments match the method's signature
                validate_arguments_against_signature(callable_, self.args, self.kwargs)
                # Call the method
                result = await callable_(*(self.args or []), **(self.kwargs or {}))
                # Set the response
                if self.is_notification:
                    self.response = NotificationResponse()
                else:
                    self.response = RequestResponse(self.request_id, result)
        # Ensure the response has been set before returning it
        assert isinstance(self.response, Response), 'Invalid response type'
        return self.response
