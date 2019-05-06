from app import db

class Filepaths(db.Model):

    __tablename__ = "filepaths"

    id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Filepaths(id={self.id}, contents={self.contents})"
