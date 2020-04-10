import base64
import os
import hashlib
import time

import settings
from facecatch.database import db


class PersonInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.String, nullable=False)
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
            'image': self.gen_img_base64(),
            'department': self.department,
            'create_time': self.create_time
        }
        return d

    def delete_person_jpg(self):
        if self.image:
            os.remove(self.image)
        return None

    def update_person_jpg(self, new_id):
        os.rename(self.person_image_path(self.id_card),
                  self.person_image_path(new_id))
        self.image = self.person_image_path(new_id)
        return None

    def gen_img_base64(self):
        with open(self.image, 'rb') as f:
            return base64.b64encode(f.read()).decode()

    def gen_image_card(self, image):
        m = hashlib.md5()
        m.update(str(time.time()).encode('utf_8'))
        card = m.hexdigest()
        path = self.write_image(image, card)
        return path

    @staticmethod
    def write_image(image, id_card):
        if not os.path.exists(settings.PERSON_STORAGE_ADDRESS):
            os.mkdir(settings.PERSON_STORAGE_ADDRESS)
        with open(settings.PERSON_STORAGE_ADDRESS + '/{}.jpg'.format(id_card), 'wb') as f:
            f.write(image)
        return settings.PERSON_STORAGE_ADDRESS + '/{}.jpg'.format(id_card)


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

