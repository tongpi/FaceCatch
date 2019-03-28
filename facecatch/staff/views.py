import base64
import json

import flask
from flask import request, render_template, redirect, url_for, flash
from flask_cas import login_required

from app import db
from facecatch.models import PersonInfo
from facecatch.staff.forms import AddForm, UpdateForm
from facecatch.utils import get_image_face


blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route("/inspect_image", methods=['GET', 'POST'])
def inspect_image():
    """ajax 校验上传图片是否符合要求"""

    result_message = "success"
    image_file = request.files['image_file']

    face_list = get_image_face(image_file.read())
    if len(face_list) != 1:
        result_message = "failed"

    return result_message


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """将录入信息处理后存储到数据库中"""

    add_form = AddForm()
    if request.method == 'POST':
        image = request.files['file'].read()
        face_list = get_image_face(image)
        # TODO: 此处用ajax处理上传图片不规范问题

        # 将录入信息存储到数据库
        person = PersonInfo(
            name=request.form['name'],
            id_card=request.form['id_card'],
            description=request.form['description'],
            face_id=str(face_list[0]['faceID']),
            image=base64.b64encode(image).decode()
            )

        db.session.add(person)
        db.session.commit()

        return redirect(url_for('facecatch.staff.views.show'))

    return render_template('staff/add.html', form=add_form)


@blueprint.route('/show', methods=['GET'])
@login_required
def show():
    """返回录入信息展示页面"""
    persons = PersonInfo.query.filter().all()
    return render_template('staff/show.html', persons=persons, bytes=bytes)


@blueprint.route('/detail/<person_id>', methods=['GET', 'POST'])
@login_required
def detail(person_id):
    """返回录入信息详情页"""

    person = PersonInfo.query.filter(PersonInfo.id == person_id).first()

    return render_template('staff/detail.html', person=person, bytes=bytes)


@blueprint.route('/delete_person/<person_id>', methods=['GET'])
@login_required
def delete_person(person_id):
    """删除指定人员信息"""

    person = PersonInfo.query.filter(PersonInfo.id == person_id).first()
    db.session.delete(person)
    db.session.commit()

    return redirect(url_for("facecatch.staff.views.show"))


@blueprint.route('/update_person/<person_id>', methods=['GET', 'POST'])
@login_required
def update_person(person_id):
    """修改指定人员的信息"""

    update_form = UpdateForm()
    person = PersonInfo.query.filter(PersonInfo.id == person_id).first()

    if request.method == 'POST':

        if request.form['name']:
            person.name = request.form['name']
        if request.form['id_card']:
            person.id_card = request.form['id_card']
        if request.form['description']:
            person.description = request.form['description']

        if 'file' not in request.form:
            image = request.files['file'].read()

            person.image = base64.b64encode(image).decode()

            person.face_id = str(get_image_face(image)[0]['faceID'])

        db.session.commit()
        flash('更新成功')
        return redirect(url_for('facecatch.staff.views.show'))

    return render_template('staff/update.html', person=person, form=update_form, bytes=bytes)



