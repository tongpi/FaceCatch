from app import db, webapp


class PersonInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    id_card = db.Column(db.String(80))
    model_id = db.Column(db.String(80))
    description = db.Column(db.String(200))
    face_feature = db.Column(db.String(200))
    similarity = db.Column(db.Float(2))
    image = db.Column(db.LargeBinary())

    __tablename__ = 'person_info'

    def to_dict(self):
        d = {
            'id': self.id,
            'name': self.name,
            'id_card': self.id_card,
            'model_id': self.model_id,
            'description': self.description,
            'face_feature': self.face_feature,
            'similarity': self.similarity,
        }
        return d


@webapp.before_first_request
def create_db():
    db.create_all()



