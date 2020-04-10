import base64
import flask
import pandas
import requests

from flask import request, render_template, redirect, url_for, flash, make_response, send_from_directory
from flask_cas import login_required

import settings
from facecatch.database import db
from facecatch.log import logger
from facecatch.models import PersonInfo
from facecatch.staff.forms import AddForm, UpdateForm, BatchAddForm
from facecatch.utils import get_image_face, get_batch_info, string_to_file, get_create_time

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
    if request.method == 'POST' and add_form.validate_on_submit():
        image = request.files['file'].read()
        PersonInfo.write_image(image, request.form['id_card'])
        face_list = get_image_face(image)

        # 将录入信息存储到数据库
        person = PersonInfo(
            name=request.form['name'],
            department=request.form['department'],
            id_card=request.form['id_card'],
            description=request.form['description'],
            face_id=str(face_list[0]['faceID']),
            image=settings.PERSON_STORAGE_ADDRESS+'/{}.jpg'.format(request.form['id_card']),
            create_time=get_create_time(),
            )

        db.session.add(person)
        db.session.commit()
        logger.info("成功添加人员信息：{}-{}".format(request.form['name'], request.form['id_card']))
        return redirect(url_for('staff.show'))

    return render_template('staff/add.html', form=add_form)


@blueprint.route('/batch_add', methods=['GET', 'POST'])
@login_required
def batch_add():
    form = BatchAddForm()
    if request.method == 'POST' and form.validate_on_submit():

        person_data = []
        if request.files['file'].filename.endswith(".zip"):
            file_zip = request.files['file'].read()
            try:
                person_list = get_batch_info(string_to_file(file_zip))
            except:
                flash('上传的zip文件不符合规范，请按示例文件重新生成格式正确的zip文件！')
                logger.error("上传的zip文件不符合规范，请按示例文件重新生成格式正确的zip文件！")
                person_list = []

            for person in person_list:
                face_list = get_image_face(person['image'])
                if isinstance(face_list, str):
                    return redirect(url_for('facecatch.error', data=face_list))
                if len(face_list) == 1:
                    person_data.append(PersonInfo(
                        name=person['name'],
                        department=person['department'],
                        id_card=person['id_card'],
                        description=person['description'],
                        face_id=str(face_list[0]['faceID']),
                        image=settings.PERSON_STORAGE_ADDRESS + '/{}.jpg'.format(person['id_card']),
                        create_time=get_create_time(),
                    ))
                else:
                    logger.error('证件号为{}的用户照片不符合规范'.format(person['id_card']))
                    flash('证件号为{}的用户照片不符合规范'.format(person['id_card']))
        elif request.files['file'].filename.endswith(".xlsx") or request.files['file'].filename.endswith(".xls"):
            excel_datas = pandas.read_excel(request.files['file']).values
            for excel_data in excel_datas:
                is_image = True
                try:
                    image = requests.get(excel_data[5]).content
                    if image[:15] == b'<!doctype html>':
                        logger.error('地址为{}的用户照片请求不到资源！'.format(excel_data[5]))
                        is_image = False
                except Exception:
                    logger.error('地址为{}的用户照片请求不到资源！'.format(excel_data[5]))
                    is_image = False
                if is_image:
                    face_list = get_image_face(image)
                    if isinstance(face_list, str):
                        return redirect(url_for('facecatch.error', data=face_list))
                    if len(face_list) == 1:
                        PersonInfo.write_image(image, excel_data[0])
                        person_data.append(PersonInfo(
                            name=excel_data[1],
                            department=excel_data[2],
                            id_card=excel_data[3],
                            description=str(excel_data[4])[:30],
                            face_id=str(face_list[0]['faceID']),
                            image=settings.PERSON_STORAGE_ADDRESS + '/{}.jpg'.format(excel_data[0]),
                            create_time=get_create_time(),
                        ))
                    else:
                        logger.error('图片ID为{}的用户照片不符合规范'.format(excel_data[0]))
                        person_data.append(PersonInfo(
                            name=excel_data[1],
                            department=excel_data[2],
                            id_card=excel_data[3],
                            description=str(excel_data[4])[:30],
                            face_id='',
                            image='',
                            create_time=get_create_time(),
                        ))
                else:
                    person_data.append(PersonInfo(
                        name=excel_data[1],
                        department=excel_data[2],
                        id_card=excel_data[3],
                        description=str(excel_data[4])[:30],
                        face_id='',
                        image='',
                        create_time=get_create_time(),
                    ))

        try:
            db.session.add_all(person_data)
            db.session.commit()
            logger.info("批量录入人员信息成功！")
        except Exception as e:
            flash('用户信息错误')
            logger.error("批量录入人员信息失败，错误：{}".format(e))

        return redirect(url_for('staff.show'))

    return render_template('staff/batch_add.html', form=form)


@blueprint.route('/show', methods=['GET'])
@login_required
def show():
    """返回录入信息展示页面"""

    page = int(request.args.get('page', 1))
    per_page = 12

    paginate = PersonInfo.query.filter().order_by(PersonInfo.id).paginate(page=page, per_page=per_page, error_out=False)
    persons = paginate.items
    for person in persons:
        if person.image == '':
            person.person_image = url_for('static', filename='image/not_found.png')
        else:
            with open(person.image, 'rb') as f:
                person.person_image = "data:image/png;base64, {}".format(base64.b64encode(f.read()).decode())
    return render_template('staff/show.html', persons=persons, paginate=paginate)


@blueprint.route('/show/unusual', methods=['GET'])
@login_required
def unusual_show():
    """返回录入信息展示页面"""

    page = int(request.args.get('page', 1))
    per_page = 12

    paginate = PersonInfo.query.filter(PersonInfo.image == '').order_by(PersonInfo.id).paginate(page=page, per_page=per_page, error_out=False)
    persons = paginate.items
    for person in persons:
        if person.image == '':
            person.person_image = url_for('static', filename='image/not_found.png')
        else:
            with open(person.image, 'rb') as f:
                person.person_image = "data:image/png;base64, {}".format(base64.b64encode(f.read()).decode())
    return render_template('staff/unusual.html', persons=persons, paginate=paginate)


@blueprint.route('/detail/<person_id>', methods=['GET', 'POST'])
@login_required
def detail(person_id):
    """返回录入信息详情页"""

    person = PersonInfo.query.filter(PersonInfo.id == person_id).first()
    if person.image == '':
        person.person_image = url_for('static', filename='image/not_found.png')
    else:
        with open(person.image, 'rb') as f:
            person.person_image = "data:image/png;base64, {}".format(base64.b64encode(f.read()).decode())
    return render_template('staff/detail.html', person=person)


@blueprint.route('/delete_person', methods=['POST'])
@login_required
def delete_person():
    """删除指定人员信息"""
    try:
        data = request.get_data().decode()
        person_id = data.split('=')[1]
        person = PersonInfo.query.filter(PersonInfo.id == int(person_id)).first()
        person.delete_person_jpg()
        db.session.delete(person)
        db.session.commit()
        logger.info("删除人员信息成功！人员ID为：{}".format(person_id))
        return "success"
    except Exception as e:
        logger.error("删除人员信息失败！原因：{}".format(e))
        return "fail"


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
        if request.form['department']:
            person.department = request.form['department']

        if 'file' not in request.form:
            image = request.files['file'].read()
            person.delete_person_jpg()
            person.image = person.gen_image_card(image)

            person.face_id = str(get_image_face(image)[0]['faceID'])

        db.session.commit()
        flash('更新成功')
        logger.info("更新人员信息成功！{}-{}".format(person.name, person.id_card))
        return redirect(url_for('staff.show'))

    if person.image == '':
        person.person_image = url_for('static', filename='image/not_found.png')
    else:
        with open(person.image, 'rb') as f:
            person.person_image = "data:image/png;base64, {}".format(base64.b64encode(f.read()).decode())
    return render_template('staff/update.html', person=person, form=update_form)


@blueprint.route('/download_file', methods=['GET', 'POST'])
@login_required
def download_file():
    response = make_response(send_from_directory('facecatch/static/sample_file', filename='face.zip', as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format('face.zip'.encode().decode('latin-1'))
    logger.info("下载示例文件。")
    return response

