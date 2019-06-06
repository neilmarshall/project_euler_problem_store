import unittest

from app import create_app, db
from app.models import Language, Problem
from tests import TestConfig


class TestSearchQueryFunctionality(unittest.TestCase):

    def setUp(self):
        # establish application context and test client
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()

        # create in-memory database structure
        db.create_all()

        # add a Language object
        self.language = Language(language_id=1, language='Python', extension='py')
        db.session.add(self.language)

        # add a Problem object
        self.problem1 = Problem(contents="arbitrary solution to problem1",
                language_id=self.language.language_id, title="problem1")
        self.problem2 = Problem(contents="arbitrary solution to problem2",
                language_id=self.language.language_id, title="problem2")
        self.problem3 = Problem(contents="arbitrary [ ] to problem3",
                language_id=self.language.language_id, title="problem3")
        db.session.add_all((self.problem1, self.problem2, self.problem3))

        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_searching_without_query_returns_index_page(self):
        response = self.test_client.get('/search', follow_redirects=False, query_string={})
        self.assertEqual(response.status_code, 302)
        actual_redirect_url = response.location.split('http://localhost')[1]
        expected_redirect_url = '/index'
        self.assertEqual(actual_redirect_url, expected_redirect_url)

    def test_searching_with_query_not_in_problems_returns_null_results_page(self):
        response = self.test_client.get('/search', follow_redirects=True,
                                        query_string={'search_for': 'missing phrase'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"Sorry - No solutions found containing phrases like 'missing phrase'" in response.data)

    def test_searching_with_query_in_problems_returns_search_results_page(self):
        response = self.test_client.get('/search', follow_redirects=True,
                                        query_string={'search_for': 'solution'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"Problem1" in response.data)
        self.assertTrue(b"Problem2" in response.data)
        self.assertFalse(b"Problem3" in response.data)
