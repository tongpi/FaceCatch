from facecatch.database import db


class PersonInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    department = db.Column(db.String())
    id_card = db.Column(db.String(80))
    description = db.Column(db.String(200))
    face_id = db.Column(db.String())
    image = db.Column(db.String())
    create_time = db.Column(db.String())

    __tablename__ = 'person_info'

    def to_dict(self):
        d = {
            'id': self.id,
            'name': self.name,
            'id_card': self.id_card,
            'description': self.description,
            'face_id': self.face_id,
            'image': self.image,
            'department': self.department,
            'create_time': self.create_time
        }
        return d


class ImageInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unknown_id = db.Column(db.Integer, db.ForeignKey("unknown_person.id"))
    label = db.Column(db.String())
    create_time = db.Column(db.String())
    image_path = db.Column(db.String())

    __tablename__ = 'image_info'

    def to_dict(self):
        d = {
            'id': self.id,
            'label': self.label,
            'modify_time': self.modify_time,
            'image_path': self.image_path,
        }

        return d


class UnknownPersonInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    face_id = db.Column(db.String())
    image_path = db.Column(db.String())

    __tablename__ = 'unknown_person'

