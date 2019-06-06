import unittest
from io import BytesIO

from app import create_app, db
from app.models import Language, Problem, User
from tests import TestConfig


class TestFileDeletion(unittest.TestCase):

    def setUp(self):
        # establish application context and test client
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = self.app.test_client()

        # create in-memory database structure
        db.create_all()

        # add a User object
        self.user1 = User(username='user1')
        self.user1.set_password('pass1')
        db.session.add(self.user1)

        # add a Language object
        self.language = Language(language_id=1, language='Python', extension='py')
        db.session.add(self.language)

        db.session.commit()

        # log in
        self.test_client.post('/', data = {'username': 'user1', 'password': 'pass1'})

        # add a problem
        self.data = {'problem_selection': 1, 'problem_title': 'a title',
                'file_upload': (BytesIO(b'file contents'), 'test.py')}
        self.test_client.post('/create_solution', data=self.data)

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_deleting_file_removes_it_from_database(self):
        self.assertEqual(Problem.query.count(), 1)
        response = self.test_client.post('/delete_solution', follow_redirects=True,
                data={'problem_selection': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 0)

    def test_deleting_non_existent_file_does_nothing(self):
        self.assertEqual(Problem.query.count(), 1)
        response = self.test_client.post('/delete_solution', follow_redirects=True,
                data={'problem_selection': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 1)
