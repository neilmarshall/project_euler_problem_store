import unittest
from io import BytesIO

from app import create_app, db
from app.models import Language, Problem, User

class TestConfig():
    SECRET_KEY = "123456"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOLUTIONS_TO_SHOW = 12
    TESTING = True
    WTF_CSRF_ENABLED = False


class TestFileCreation(unittest.TestCase):

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

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_uploading_valid_file_adds_file(self):
        data = {'problem_selection': 1, 'problem_title': 'a title',
                'file_upload': (BytesIO(b'file contents'), 'test.py')}
        response = self.test_client.post('/create_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        db_problem = Problem.query.first()
        self.assertEqual(Problem.query.count(), 1)
        self.assertEqual(db_problem.title, data['problem_title'])
        self.assertEqual(db_problem.contents, 'file contents')
        self.assertEqual(db_problem.language_id, self.language.language_id)

    def test_uploading_file_with_invalid_extension_does_not_add_file(self):
        data = {'problem_selection': 1, 'problem_title': 'a title',
                'file_upload': (BytesIO(b'file contents'), 'test.invalid')}
        response = self.test_client.post('/create_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 0)

    def test_uploading_file_without_ID_does_not_add_file(self):
        data = {'problem_selection': 1, 'problem_title': 'a title',
                'file_upload': (BytesIO(b'file contents'), 'test.py')}
        response = self.test_client.post('/create_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 0)

    def test_uploading_file_without_ID_does_not_add_file(self):
        data = {'problem_title': 'a title', 'file_upload': (BytesIO(b'file contents'), 'test.py')}
        response = self.test_client.post('/create_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 0)

    def test_uploading_file_without_title_does_not_add_file(self):
        data = {'problem_selection': 1, 'file_upload': (BytesIO(b'file contents'), 'test.py')}
        response = self.test_client.post('/create_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 0)

    def test_uploading_file_without_content_does_not_add_file(self):
        data = {'problem_selection': 1, 'problem_title': 'a title'}
        response = self.test_client.post('/create_solution', follow_redirects=True, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Problem.query.count(), 0)

    def test_uploading_file_with_duplicate_ID_does_not_add_file(self):
        data1 = {'problem_selection': 1, 'problem_title': 'title_1',
                 'file_upload': (BytesIO(b'file contents 1'), 'test.py')}
        data2 = {'problem_selection': 1, 'problem_title': 'title_2',
                 'file_upload': (BytesIO(b'file contents 2'), 'test.py')}
        self.test_client.post('/create_solution', follow_redirects=True, data=data1)
        self.test_client.post('/create_solution', follow_redirects=True, data=data2)
        self.assertEqual(Problem.query.count(), 1)
