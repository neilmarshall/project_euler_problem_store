from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login

class Problem(db.Model):

    __tablename__ = "problems"

    problem_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    contents = db.Column(db.Text, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.language_id'), nullable=False)

    def __repr__(self):
        return f"Problem(problem_id={self.problem_id}, title='{self.title}', " + \
               f"contents='{self.contents}', language_id={self.language_id})"


class Language(db.Model):

    __tablename__ = "languages"

    language_id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(16), nullable=False)
    extension = db.Column(db.String(16), nullable=False)

    def __repr__(self):
        return f"Languages(language_id={self.language_id}, language='{self.language}', " + \
               f"extension='{self.extension}')"


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
