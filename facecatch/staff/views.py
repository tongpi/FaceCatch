import base64

import flask
from flask import request, render_template, redirect, url_for, flash, session
from flask_cas import login_required

from app import db
from facecatch.models import PersonInfo
from facecatch.staff.forms import AddForm, UpdateForm
from facecatch.utils import get_feature


blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """将录入信息处理后存储到数据库中"""

    add_form = AddForm()
    model_id = session['model_id']
    if request.method == 'POST':
        image = request.files['file'].read()

        face_feature, similarity = get_feature(image, model_id)

        # 将录入信息存储到数据库
        person = PersonInfo(
            name=request.form['name'],
            id_card=request.form['id_card'],
            description=request.form['description'],
            model_id=model_id,
            face_feature=face_feature,
            similarity=similarity,
            image=image
            )

        db.session.add(person)
        db.session.commit()

        return redirect(url_for('facecatch.staff.views.show'))

    return render_template('staff/add.html', form=add_form)


@blueprint.route('/show', methods=['GET'])
@login_required
def show():
    """返回录入信息展示页面"""
    persons = PersonInfo.query.filter(PersonInfo.model_id == session['model_id'])

    return render_template('staff/show.html', persons=persons, base64=base64)


@blueprint.route('/detail/<person_id>', methods=['GET', 'POST'])
@login_required
def detail(person_id):
    """返回录入信息详情页"""

    person = PersonInfo.query.filter(PersonInfo.id == person_id).first()
    image = base64.b64encode(person.image).decode('utf-8')

    return render_template('staff/detail.html', person=person, image=image)


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
            try:
                image = request.files['file'].read()
            except Exception:
                image = None

            person.image = image
            face_feature, similarity = get_feature(image, session['model_id'])
            person.face_feature = face_feature
            person.similarity = similarity

        db.session.commit()
        flash('更新成功')
        return redirect(url_for('facecatch.staff.views.show'))

    return render_template('staff/update.html', person=person, form=update_form, base64=base64)
