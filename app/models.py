from app import db

class Filepaths(db.Model):

    __tablename__ = "filepaths"

    id = db.Column(db.Integer, primary_key=True)
    filepath = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return f"Filepaths({self.id}, {self.filepath})"
