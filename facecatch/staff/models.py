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