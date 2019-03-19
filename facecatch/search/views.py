import base64

import flask
from flask import request, render_template, session
from flask_cas import login_required

from facecatch.models import PersonInfo
from facecatch.search.forms import UploadForm
from facecatch.utils import get_feature


blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """将上传的图片进行比对"""

    upload_form = UploadForm()
    return render_template('search/search.html',
                           form=upload_form,
                           base64=base64,)


@blueprint.route('/search', methods=['POST'])
def search():
    upload_form = UploadForm()

    upload_file = request.files['file'].read()
    face_feature, similarity = get_feature(upload_file, session['model_id'])

    if similarity > 70:
        person = PersonInfo.query.filter(PersonInfo.face_feature == face_feature, PersonInfo.model_id == session['model_id']).first()
        if person:
            person_info = person
            return render_template('search/search.html', form=upload_form, base64=base64, person=person_info, image=upload_file)

    match_result = '该人员信息未知。'
    return render_template(
            'search/search.html',
            form=upload_form,
            base64=base64,
            image=upload_file,
            match_result=match_result)




