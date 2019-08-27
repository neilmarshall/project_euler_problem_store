import unittest
from io import BytesIO

from app import create_app, db
from app.models import Language, Problem, User
from tests import TestConfig


class TestFileUpdating(unittest.TestCase):

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

    def test_updating_file_without_specifiying_title_overrides_contents_only(self):
        data = {'problem_selection': 1, 'file_update': (BytesIO(b'new contents'), 'test.py')}
        response = self.test_client.post('/update_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        db_problem = Problem.query.first()
        self.assertEqual(Problem.query.count(), 1)
        self.assertEqual(db_problem.title, self.data['problem_title'])
        self.assertEqual(db_problem.contents, 'new contents')
        self.assertEqual(db_problem.language_id, self.language.language_id)

    def test_updating_file_overrides_contents_and_title(self):
        data = {'problem_selection': 1, 'problem_title': 'new title',
                'file_update': (BytesIO(b'new contents'), 'test.py')}
        response = self.test_client.post('/update_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        db_problem = Problem.query.first()
        self.assertEqual(Problem.query.count(), 1)
        self.assertEqual(db_problem.title, 'new title')
        self.assertEqual(db_problem.contents, 'new contents')
        self.assertEqual(db_problem.language_id, self.language.language_id)

    def test_updating_non_existent_file_does_nothing(self):
        data = {'problem_selection': 2, 'problem_title': 'new title',
                'file_update': (BytesIO(b'new contents'), 'test.py')}
        response = self.test_client.post('/update_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        db_problem = Problem.query.first()
        self.assertEqual(Problem.query.count(), 1)
        self.assertEqual(db_problem.title, self.data['problem_title'])
        self.assertEqual(db_problem.contents, 'file contents')
        self.assertEqual(db_problem.language_id, self.language.language_id)

    def test_updating_file_without_content_does_not_update_file(self):
        data = {'problem_selection': 1, 'problem_title': 'a title',
                'file_update': (BytesIO(b''), 'test.py')}
        response = self.test_client.post('/update_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 1)
        self.assertTrue("File must not be empty" in str(response.data, 'utf-8'))
