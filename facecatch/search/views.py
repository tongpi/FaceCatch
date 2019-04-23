import base64
import flask

from flask import request, render_template, session
from flask_cas import login_required

from flask_cas import CAS
from facecatch.search.forms import UploadForm
from facecatch.utils import get_image_face, get_same_person


blueprint = flask.Blueprint('search', __name__)
cas = CAS()


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """将上传的图片进行比对"""
    session['username'] = cas.username

    upload_form = UploadForm()
    return render_template('search/search.html',
                           form=upload_form,
                           base64=base64,)


@blueprint.route('/search', methods=['POST'])
@login_required
def search():
    upload_form = UploadForm()
    upload_file = request.files['file'].read()
    face_list = get_image_face(upload_file)
    if len(face_list) >= 1:
        person, distance = get_same_person(face_list[0]['faceID'])
        if distance < 0.7:
            person_info = person
            return render_template('search/search.html', form=upload_form, person=person_info, image=upload_file, base64=base64)
        else:
            match_result = '该人员信息未知。'
    else:
        match_result = '信息未知。'

    return render_template(
            'search/search.html',
            form=upload_form,
            image=upload_file,
            match_result=match_result,
            base64=base64)




