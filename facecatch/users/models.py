from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(320), unique=True)
    password = db.Column(db.String(80))


