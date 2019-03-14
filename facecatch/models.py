from app import webapp
from app import db


class PersonInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    id_card = db.Column(db.String(80))
    description = db.Column(db.String(200))
    face_feature = db.Column(db.String(200))
    similarity = db.Column(db.Float(2))
    image = db.Column(db.LargeBinary())

    __tablename__ = 'person_info'

    def __repr__(self):
        return '<User %r>' % self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))


@webapp.before_first_request
def create_db():
    db.create_all()
