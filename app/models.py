from app import db

class Problem(db.Model):

    __tablename__ = "problems"

    problem_id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Filepaths(id={self.id}, contents={self.contents})"
