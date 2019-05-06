from app import db

class Problem(db.Model):

    __tablename__ = "problems"

    problem_id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.Text, nullable=False)
    language = db.Column(db.Integer, db.ForeignKey('languages.language_id'), nullable=False)

    def __repr__(self):
        return f"Problem(problem_id={self.id}, contents={self.contents})"


class Language(db.Model):

    __tablename__ = "languages"

    language_id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(16), nullable=False)

    problems = db.relationship('Filepaths', lazy=True, backref='language')

    def __repr__(self):
        return f"Languages(language_id={self.language_id}, language={self.language})"
