import base64
import datetime
import operator
import os
import tempfile
import time
import zipfile
import glob
import numpy
import pandas
import requests
import json

from functools import wraps
from flask import session, redirect, url_for, request

import settings
from facecatch.database import db
from .models import PersonInfo, ImageInfo

BAD_EUCLIDEAN_DISTANCE = 1

FACENET_EMOTION_DICT = {
    'Angry': '生气',
    'Sad': '悲伤',
    'Neutral': '平静',
    'Disgust': '厌烦',
    'Surprise': '惊讶',
    'Fear': '害怕',
    'Happy': '开心',
    'unknown': '未知'
}


def get_image_face(image_file, base=None):
    """根据图片路径获取图像中人脸及特征"""

    # 获取facenet 服务地址
    url = settings.FACENET_URL
    if base:
        image = image_file
    else:
        image = base64.b64encode(image_file).decode()

    data = {"data": [image]}
    # 发送请求调用facenet服务获取图像中包含的人脸信息
    req = requests.post(url, json=data)
    face_list = json.loads(req.content.decode('utf-8'))['data']
    if face_list:
        return face_list
    return None


def get_same_person(face_id):
    """获取库中相同的人的信息face_id 为列表，返回距离最小的人信息及人脸距离"""

    # 获取人脸库中的所有人的信息
    person_list = PersonInfo.query.filter().all()
    # 用于保存对比人脸的结果key:欧式距离 value: 人信息的对象
    person_dict = {}
    if not person_list:
        return None, BAD_EUCLIDEAN_DISTANCE
    for person in person_list:
        face_distance = get_face_distance(face_id, person.face_id)
        person_dict[face_distance] = person
    return person_dict[min(person_dict)], min(person_dict)


def get_person_emotion(emotion):
    """
    :param emotion: 返回表情的字典
    :return: 返回一个元组的格式（表情类型：分析值）
    """

    sort_emotion = sorted(emotion.items(), key=operator.itemgetter(1), reverse=True)[0]
    return sort_emotion


def get_face_distance(face_id1, face_id2):
    """获取两张人脸的欧式距离face_id1,face_id2 为128位的列表"""

    # 计算欧式距离
    distance = numpy.linalg.norm(numpy.array(face_id1, dtype=float) - numpy.array(eval(face_id2), dtype=float))

    return distance


def get_batch_info(file):
    """
    zip文件格式：
        一个excel文件与一个image文件夹，
        image文件夹里的内容为以人员证件号命名的png/jpg图片。

    :param file: zip文件
    :return: 返回所有人员信息的列表，列表中每个字典为每个人员的详细信息
    """

    # 打开压缩文件
    file_zip = zipfile.ZipFile(file)

    # 获取excel表对象
    excel_file = file_zip.open('{}face.xlsx'.format(file_zip.namelist()[0]))

    # 读取excel表的数据
    excel_datas = pandas.read_excel(excel_file).values

    result = []
    for excel_data in excel_datas:
        result_dict = dict()
        result_dict['name'] = excel_data[0]
        result_dict['department'] = excel_data[1]
        result_dict['id_card'] = excel_data[2]
        result_dict['description'] = excel_data[3]
        try:
            result_dict['image'] = file_zip.open('face/image/{}.png'.format(excel_data[2])).read()
        except KeyError:
            result_dict['image'] = file_zip.open('face/image/{}.jpg'.format(excel_data[2])).read()
        result.append(result_dict)

    file_zip.close()
    return result


def string_to_file(string):
    """
    将bytes流转为临时文件
    """
    file_like_obj = tempfile.NamedTemporaryFile()
    file_like_obj.write(string)
    # 确保string立即写入文件
    file_like_obj.flush()
    # 将文件读取指针返回到文件开头位置
    file_like_obj.seek(0)
    return file_like_obj


# 登录装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('center.views.login', next=request.url))

    return wrapper


def get_file_create_time(file):
    """获取文件创建时间"""
    return str(os.path.getctime(file))


def get_create_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


# 预处理图片,存入数据库中
def pretreatment_image(app):
    with app.app_context():
        try:
            # 获取预处理图片表中最大的创建时间，用于筛选处理图片范围
            max_create_time = ImageInfo.query.order_by(db.desc("create_time")).first().create_time
        except AttributeError:
            max_create_time = None
        image_path = settings.PRETREATMENT_IMAGE_PATH
        if image_path:
            jpg_path = glob.glob(image_path + "/*.jpg")
            png_path = glob.glob(image_path + "/*.png")
            # 获取所有图片的路径
            file_list = jpg_path + png_path
            for file in file_list:
                # 获取文件创建时间
                file_create_time = get_file_create_time(file)
                if max_create_time and file_create_time <= max_create_time:
                    continue
                with open(file, 'rb') as f:
                    file_b64 = base64.b64encode(f.read()).decode("utf-8")
                    face_list = get_image_face(file_b64, "true")
                    if face_list:
                        face_id = face_list[0]['faceID']
                        person, distance = get_same_person(face_id)
                        if distance < 0.9:
                            image_info = ImageInfo(
                                label=person.name,
                                create_time=file_create_time,
                                image_path=file,
                            )
                            db.session.add(image_info)
                            db.session.commit()
    print("执行完毕，时间： " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    return None
# def pretreatment_image(app):
#     with app.app_context():
#         image_path = settings.PRETREATMENT_IMAGE_PATH
#         if image_path:
#             jpg_path = glob.glob(image_path + "/*.jpg")
#             png_path = glob.glob(image_path + "/*.png")
#             file_list = jpg_path + png_path
#             for file in file_list:
#                 with open(file, 'rb') as f:
#                     file_b64 = base64.b64encode(f.read()).decode("utf-8")
#                     face_list = get_image_face(file_b64, "true")
#                     if face_list:
#                         face_id = face_list[0]['faceID']
#                         image_info = ImageInfo(
#                             face_id=str(face_id),
#                             image=file_b64
#                         )
#                         db.session.add(image_info)
#                         db.session.commit()
#                 os.remove(file)
#     print("执行完毕，时间： " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])


def get_same_image(label):
    image_info_list = ImageInfo.query.filter(ImageInfo.label == label).all()

    image_list = []
    for image_info in image_info_list:
        image_list.append(image_info.image_path)
    return image_list
# def get_same_image(face_id):
#     image_info_list = ImageInfo.query.filter().all()
#
#     image_list = []
#     if not image_info_list:
#         return None, BAD_EUCLIDEAN_DISTANCE
#     for image_info in image_info_list:
#         face_distance = get_face_distance(face_id, image_info.face_id)
#         if face_distance < 1:
#             image_list.append(image_info)
#     return image_list



