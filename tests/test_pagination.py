import unittest

from bs4 import BeautifulSoup

from app import create_app, db
from app.models import Language, Problem, User

class TestConfig():
    SECRET_KEY = "123456"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOLUTIONS_TO_SHOW = 5
    TESTING = True
    WTF_CSRF_ENABLED = False


class TestPagination(unittest.TestCase):

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
        self.language1 = Language(language_id=1, language='Python', extension='py')
        self.language2 = Language(language_id=2, language='C++', extension='cpp')
        db.session.add_all([self.language1, self.language2])

        # add Problem objects
        for _ in range(10):
            p1 = Problem(contents="contents", language_id=self.language1.language_id, title="title")
            p2 = Problem(contents="contents", language_id=self.language2.language_id, title="title")
            db.session.add_all([p1, p2])

        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_initial_page_has_correct_number_of_links(self):
        response = self.test_client.get('/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        rows = soup.find(id='links_table').find_all('tr')
        self.assertEqual(len(rows), TestConfig.SOLUTIONS_TO_SHOW)

    @unittest.skip('tbc')
    def test_accessing_landing_page_returns_status_code_200(self):
        response = self.test_client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @unittest.skip('tbc')
    def test_logging_on_with_incorrect_username_redirects_correctly(self):
        data = {'username': 'incorrect_user', 'password': 'pass1'}
        response = self.test_client.post('/', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Username not recognised or invalid password provided - please try again' in response.data)

    @unittest.skip('tbc')
    def test_logging_on_with_incorrect_password_redirects_correctly(self):
        data = {'username': 'user1', 'password': 'incorrect_password'}
        response = self.test_client.post('/', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Username not recognised or invalid password provided - please try again' in response.data)

    @unittest.skip('tbc')
    def test_logging_on_with_correct_details_redirects_correctly(self):
        data = {'username': 'user1', 'password': 'pass1'}
        response = self.test_client.post('/', data=data, follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'<a href="/logout" class="btn btn-light">Logout</a>' in response.data)
        self.assertTrue(b'<a href="/create_solution" class="btn btn-light">Create Solution</a>' in response.data)
        self.assertTrue(b'<a href="/update_solution" class="btn btn-light">Update Solution</a>' in response.data)
        self.assertTrue(b'<a href="/delete_solution" class="btn btn-light">Delete Solution</a>' in response.data)

    @unittest.skip('tbc')
    def test_logout_logs_out_user(self):
        data = {'username': 'user1', 'password': 'pass1'}
        self.test_client.post('/', data=data, follow_redirects=True)
        response = self.test_client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(b'<a href="/logout" class="btn btn-light">Logout</a>' in response.data)
        self.assertFalse(b'<a href="/create_solution" class="btn btn-light">Create Solution</a>' in response.data)
        self.assertFalse(b'<a href="/update_solution" class="btn btn-light">Update Solution</a>' in response.data)
        self.assertFalse(b'<a href="/delete_solution" class="btn btn-light">Delete Solution</a>' in response.data)
