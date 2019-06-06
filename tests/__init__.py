class TestConfig():
    SECRET_KEY = "123456"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOLUTIONS_TO_SHOW = 12
    TESTING = True
    WTF_CSRF_ENABLED = False


