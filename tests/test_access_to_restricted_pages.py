import unittest

from app import create_app
from tests import TestConfig

class TestAccessToRestrictedPages(unittest.TestCase):

    def setUp(self):
        # establish application context and test client
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_accessing_create_solution_page_without_logging_in_returns_status_code_401(self):
        response = self.test_client.get('/create_solution', follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_accessing_update_solution_page_without_logging_in_returns_status_code_401(self):
        response = self.test_client.get('/update_solution', follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_accessing_delete_solution_page_without_logging_in_returns_status_code_401(self):
        response = self.test_client.get('/delete_solution', follow_redirects=True)
        self.assertEqual(response.status_code, 401)
