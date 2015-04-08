"""test_status.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

from unittest import TestCase, main

from jsonrpcserver import status


class TestStatus(TestCase):

    def test_is_http_client_error(self):
        self.assertEqual(True, status.is_http_client_error(status.HTTP_400_BAD_REQUEST))
        self.assertEqual(False, status.is_http_client_error(status.HTTP_500_INTERNAL_ERROR))

if __name__ == '__main__':
    main()
