from unittest import TestCase

from jsonrpcserver import status


class TestStatus(TestCase):
    def test_is_http_client_error(self):
        self.assertEqual(True, status.is_http_client_error(status.HTTP_BAD_REQUEST))
        self.assertEqual(False, status.is_http_client_error(status.HTTP_INTERNAL_ERROR))
