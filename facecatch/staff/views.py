import base64

import flask

from flask import request, render_template, redirect, url_for, flash, make_response, send_from_directory
from flask_cas import login_required

from facecatch.database import db
from facecatch.models import PersonInfo
from facecatch.staff.forms import AddForm, UpdateForm, BatchAddForm
from facecatch.utils import get_image_face, get_batch_info, string_to_file

blueprint = flask.Blueprint('staff', __name__)


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

        return redirect(url_for('staff.show'))

    return render_template('staff/add.html', form=add_form)


@blueprint.route('/batch_add', methods=['GET', 'POST'])
@login_required
def batch_add():
    form = BatchAddForm()
    if request.method == 'POST':
        file_zip = request.files['file'].read()
        try:
            person_list = get_batch_info(string_to_file(file_zip))
        except:
            flash('上传的ZIP文件不符合规范')
            person_list = []

        person_data = []
        for person in person_list:
            face_list = get_image_face(person['image'])
            if len(face_list) == 1:
                person_data.append(PersonInfo(
                    name=person['name'],
                    id_card=person['id_card'],
                    description=person['description'],
                    face_id=str(face_list[0]['faceID']),
                    image=base64.b64encode(person['image']).decode()
                ))
            else:
                flash('证件号为{}的用户照片不符合规范'.format(person['id_card']))

        try:
            db.session.add_all(person_data)
            db.session.commit()
        except:
            flash('用户信息错误')

        return redirect(url_for('staff.show'))

    return render_template('staff/batch_add.html', form=form)


@blueprint.route('/show', methods=['GET'])
@login_required
def show():
    """返回录入信息展示页面"""
    persons = PersonInfo.query.filter().all()
    return render_template('staff/show.html', persons=persons)


@blueprint.route('/detail/<person_id>', methods=['GET', 'POST'])
@login_required
def detail(person_id):
    """返回录入信息详情页"""

    person = PersonInfo.query.filter(PersonInfo.id == person_id).first()

    return render_template('staff/detail.html', person=person)


@blueprint.route('/delete_person', methods=['POST'])
@login_required
def delete_person():
    """删除指定人员信息"""
    data = request.get_data().decode()
    person_id = data.split('=')[1]
    person = PersonInfo.query.filter(PersonInfo.id == int(person_id)).first()
    db.session.delete(person)
    db.session.commit()

    return "success"


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
        return redirect(url_for('staff.show'))

    return render_template('staff/update.html', person=person, form=update_form)


@blueprint.route('/download_file', methods=['GET', 'POST'])
@login_required
def download_file():
    response = make_response(send_from_directory('facecatch/static/sample_file', filename='face.zip', as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format('face.zip'.encode().decode('latin-1'))
    return response

