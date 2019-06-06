"""
Definition of all object-relational models
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

class Problem(db.Model):
    """Object-relational model of Project Euler problems"""

    __tablename__ = "problems"

    problem_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    contents = db.Column(db.Text, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.language_id'), nullable=False)

    def __repr__(self):
        return f"Problem(problem_id={self.problem_id}, title='{self.title}', " + \
               f"contents='{self.contents}', language_id={self.language_id})"

    def __eq__(self, other):
        if not isinstance(other, Problem):
            return False
        return self.title == other.title and self.contents == other.contents and \
            self.language_id == other.language_id


class Language(db.Model):
    """Object relational model of programming languages and file extensions"""

    __tablename__ = "languages"

    language_id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(16), nullable=False)
    extension = db.Column(db.String(16), nullable=False)

    problems = db.relationship('Problem', backref='language')

    def __repr__(self):
        return f"Languages(language_id={self.language_id}, language='{self.language}', " + \
               f"extension='{self.extension}')"

    def __eq__(self, other):
        if not isinstance(other, Language):
            return False
        return self.language == other.language and self.extension == other.extension


class User(UserMixin, db.Model):
    """Object relational model of users"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"

    def set_password(self, password):
        """Set a password for a user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Assert whether a given password matches the hash of the stored password"""
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    """'load_user' function required by flask_login"""
    return User.query.get(int(user_id))
