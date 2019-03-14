import base64

import flask
from flask import request, render_template, redirect, url_for

from facecatch.models import PersonInfo
from facecatch.search.forms import UploadForm
from facecatch.utils import get_feature


blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    """将上传的图片进行比对"""

    upload_file = ''
    match_result = ''
    upload_form = UploadForm()
    if request.method == 'POST':
        upload_file = request.files['file'].read()
        face_feature, similarity = get_feature(upload_file)

        if similarity > 70:
            person = PersonInfo.query.filter(PersonInfo.face_feature == face_feature).first()
            if person:
                match_result = person
            else:
                match_result = '该人员信息未知。'
        else:
            match_result = '该人员信息未知。'

    return render_template('search/upload.html',
                           form=upload_form,
                           base64=base64,
                           image=upload_file,
                           match_result=match_result)
