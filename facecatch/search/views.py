import base64
import flask

from flask import request, render_template, session, jsonify, current_app, redirect, flash
from flask_cas import login_required
from flask_restful import Resource

from flask_cas import CAS
from facecatch.search.forms import UploadForm
from facecatch.utils import get_image_face, get_same_person, get_same_image, pretreatment_image


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
    if face_list:
        person, distance = get_same_person(face_list[0]['faceID'])
        if distance < 0.9:
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


@blueprint.route('/pretreatment', methods=['GET'])
@login_required
def pretreatment():
    pretreatment_image(current_app)
    flash("预处理完成")
    return redirect('/')


class ImageList(Resource):

    def post(self):
        """
        需要发送一个以data为键，base64图片为值的键值对的请求
        :return:返回匹配到的所有图片的base64格式
        """
        try:
            data = eval(request.get_data().decode('utf8'))['data']
        except:
            data = request.get_data().decode('utf8')
        face_list = get_image_face(data, 'true')
        if face_list:
            person, distance = get_same_person(face_list[0]['faceID'])
            if distance < 0.9:
                label = person.name
                # face_id = face_list[0]['faceID']
                # image_list = get_same_image(face_id)
                image_list = get_same_image(label)
                return [m for m in image_list]
        return jsonify({"error": "传入的照片不符合规范"})


