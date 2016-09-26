"""Asynchronous request"""

from .request import Request
from .response import ExceptionResponse, NotificationResponse, RequestResponse

class AsyncRequest(Request):
    """Asynchronous request"""

    async def call(self, methods):
        """Find the method from the passed list, and call it, returning a
        Response"""
        # Validation or parsing may have failed in __init__, in which case
        # there's no point calling. It would've already set the response.
        if not self.response:
            # call_context handles setting the result/exception of the call
            with self.handle_exceptions():
                # Get the method object from a list (raises MethodNotFound)
                callable_ = self._get_method(methods, self.method_name)
                # Ensure the arguments match the method's signature
                self._validate_arguments_against_signature(callable_)
                # Call the method
                result = await callable_(*(self.args or []),
                                         **(self.kwargs or {}))
                # Set the response
                if self.is_notification:
                    self.response = NotificationResponse()
                else:
                    self.response = RequestResponse(self.request_id, result) #pylint:disable=redefined-variable-type
        # Ensure the response has been set
        assert self.response, 'Call must set response'
        assert isinstance(self.response, (ExceptionResponse, \
            NotificationResponse, RequestResponse)), 'Invalid response type'
        return self.response
