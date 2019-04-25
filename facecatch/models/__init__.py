from facecatch.database import db


class PersonInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    id_card = db.Column(db.String(80))
    description = db.Column(db.String(200))
    face_id = db.Column(db.String())
    image = db.Column(db.String())

    __tablename__ = 'person_info'

    def to_dict(self):
        d = {
            'id': self.id,
            'name': self.name,
            'id_card': self.id_card,
            'description': self.description,
            'face_id': self.face_id,
        }
        return d






