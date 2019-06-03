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
        self.language3 = Language(language_id=3, language='F#', extension='fs')
        self.language4 = Language(language_id=4, language='F#', extension='fsx')
        db.session.add_all([self.language1, self.language2, self.language3, self.language4])

        # add Problem objects
        for _ in range(10):
            p1 = Problem(contents="contents", language_id=self.language1.language_id, title="title")
            p2 = Problem(contents="contents", language_id=self.language2.language_id, title="title")
            db.session.add_all([p1, p2])

        f1 = Problem(contents='contents', language_id=self.language3.language_id, title='title')
        f2 = Problem(contents='contents', language_id=self.language4.language_id, title='title')
        db.session.add_all([f1, f2])

        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_first_page_has_correct_links(self):
        response = self.test_client.get('/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        contents = [row.text.strip() for row in soup.find(id='links_table').find_all('tr')]
        self.assertEqual(len(contents), TestConfig.SOLUTIONS_TO_SHOW)
        self.assertEqual(contents, [f'Problem{i} - title' for i in range(1, TestConfig.SOLUTIONS_TO_SHOW + 1)])

    def test_second_page_has_correct_links(self):
        response = self.test_client.get('/?page=2')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        contents = [row.text.strip() for row in soup.find(id='links_table').find_all('tr')]
        self.assertEqual(len(contents), TestConfig.SOLUTIONS_TO_SHOW)
        self.assertEqual(contents, [f'Problem{i} - title' for i in range(TestConfig.SOLUTIONS_TO_SHOW + 1, TestConfig.SOLUTIONS_TO_SHOW * 2 + 1)])

    def test_html_from_first_page_next_link_has_correct_links(self):
        response = self.test_client.get('/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        next_link = soup.find(id="next_link")["href"]
        response = self.test_client.get(next_link)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        contents = [row.text.strip() for row in soup.find(id='links_table').find_all('tr')]
        self.assertEqual(len(contents), TestConfig.SOLUTIONS_TO_SHOW)
        self.assertEqual(contents, [f'Problem{i} - title' for i in range(TestConfig.SOLUTIONS_TO_SHOW + 1, TestConfig.SOLUTIONS_TO_SHOW * 2 + 1)])

    def test_first_page_with_language_filter_has_correct_links(self):
        response = self.test_client.get(f'/?language_filter={self.language1.language}')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        contents = [row.text.strip() for row in soup.find(id='links_table').find_all('tr')]
        self.assertEqual(len(contents), TestConfig.SOLUTIONS_TO_SHOW)
        self.assertEqual(contents, [f'Problem{i} - title' for i in range(1, 2 * TestConfig.SOLUTIONS_TO_SHOW + 1, 2)])

    def test_html_from_first_page_next_link_with_language_filter_has_correct_links(self):
        response = self.test_client.get(f'/?language_filter={self.language1.language}')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        next_link = soup.find(id="next_link")["href"]
        response = self.test_client.get(next_link)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        contents = [row.text.strip() for row in soup.find(id='links_table').find_all('tr')]
        self.assertEqual(len(contents), TestConfig.SOLUTIONS_TO_SHOW)
        self.assertEqual(contents, [f'Problem{i} - title' for i in range(2 * TestConfig.SOLUTIONS_TO_SHOW + 1, 4 * TestConfig.SOLUTIONS_TO_SHOW + 1, 2)])

    def test_filter_list_does_not_show_duplicate_languages(self):
        response = self.test_client.get('/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        options = [option.text for option in soup.find(id="language_filter").find_all("option")]
        self.assertEqual(options, ['No filter', 'Python', 'C++', 'F#'])
