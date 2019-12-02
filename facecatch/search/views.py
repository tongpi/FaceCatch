import base64
from threading import Thread

import flask

from flask import request, render_template, session, jsonify, current_app, redirect, flash
from flask_cas import login_required
from flask_restful import Resource

from flask_cas import CAS

from facecatch.database import db
from facecatch.log import logger
from facecatch.models import UnknownPersonInfo, PersonInfo
from facecatch.search.forms import UploadForm
from facecatch.utils import get_image_face, get_same_person, get_same_image, pretreatment_image, get_create_time

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
                           base64=base64)


@blueprint.route('/search', methods=['POST'])
@login_required
def search():
    upload_form = UploadForm()
    upload_file = request.files['file'].read()
    face_list = get_image_face(upload_file)
    if face_list:
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


@blueprint.route('/pretreatment', methods=['GET'])
@login_required
def pretreatment():
    app = current_app._get_current_object()
    pre_job = Thread(target=pretreatment_image, args=[app])
    pre_job.start()
    return redirect('/')


class ImageListResource(Resource):

    def post(self):
        """
        需要发送一个以data为键，base64图片为值的键值对的请求
        :return:返回匹配到的所有相似的特征图片
        """
        if request.get_json():
            path = request.get_json()['path']
        else:
            logger.error("获取图片列表：请求中的数据格式不是JSON格式！")
            return jsonify({"error": "请发送json格式的数据。"})

        try:
            with open(path, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            logger.error("获取图片列表：根据请求中的图片地址未找到图片！")
            return jsonify({"error": "传入的路径不正确。"})

        face_list = get_image_face(data)
        if face_list:
            person, distance = get_same_person(face_list[0]['faceID'])
            if distance < 0.8:
                logger.info("获取图片列表成功！（已知人员）")
                return get_same_image(person.name)
            person, distance = get_same_person(face_list[0]['faceID'], "unknown")
            if distance < 0.8:
                logger.info("获取图片列表成功！（未知人员）")
                return get_same_image(person.name)
        logger.error("获取图片列表：传入的照片未能检测出人脸特征或人脸特征极不明显！")
        return jsonify({"error": "传入的照片不符合规范"})


class ImageResource(Resource):

    def post(self, unknown_id):
        if unknown_id:
            unknown_info = UnknownPersonInfo.query.filter(UnknownPersonInfo.id == unknown_id).first()
            person = PersonInfo(
                name=request.form['name'],
                department=request.form['department'],
                id_card=request.form['id_card'],
                description=request.form['description'],
                face_id=unknown_info.face_id,
                image=unknown_info.image_path,
                create_time=get_create_time(),
            )
            db.session.add(person)
            db.session.commit()
            return "{}已添加到人员信息库".format(request.form['name'])
        return jsonify({"error": "缺少参数"})






