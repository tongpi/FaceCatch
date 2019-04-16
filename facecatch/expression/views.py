import base64
import flask

from flask import render_template, request

from facecatch.search.forms import UploadForm
from facecatch.utils import get_image_face, get_person_emotion, FACENET_EMOTION_DICT

blueprint = flask.Blueprint('expression', __name__)


@blueprint.route('/expression', methods=['POST', 'GET'])
def expression():
    upload_form = UploadForm()
    if request.method == 'POST':
        upload_file = request.files['file'].read()
        face_list = get_image_face(upload_file)
        if len(face_list) >= 1:
            emotion = get_person_emotion(face_list[0]['emotion'])[0]
        else:
            emotion = 'unknown'
        return render_template('expression/expression.html',
                               form=upload_form,
                               image=upload_file,
                               emotion=FACENET_EMOTION_DICT[emotion],
                               base64=base64)
    return render_template('expression/expression.html',
                           form=upload_form,
                           base64=base64)


