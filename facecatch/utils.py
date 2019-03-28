import base64

import numpy
import requests
import json

from functools import wraps
from flask import session, redirect, url_for, request

import settings
from .models import PersonInfo


def get_path_face(image_path):
    """根据图片获取图像中人脸及特征"""

    url = settings.FACENET_URL
    data = {"data":image_path}
    req = requests.post(url, json=data)
    face_list = json.loads(req.content.decode('utf-8'))['data']
    return face_list


def get_image_face(image_file):
    """根据图片路径获取图像中人脸及特征"""

    # 获取facenet 服务地址
    url = settings.FACENET_URL
    image = base64.b64encode(image_file).decode()
    data = {"data": [image]}
    # 发送请求调用facenet服务获取图像中包含的人脸信息
    req = requests.post(url, json=data)
    face_list = json.loads(req.content.decode('utf-8'))['data']
    return face_list


def get_same_person(face_id):
    """获取库中相同的人的信息face_id 为列表，返回距离最小的人信息及人脸距离"""

    # 获取人脸库中的所有人的信息
    person_list = PersonInfo.query.filter().all()
    # 用于保存对比人脸的结果key:欧式距离 value: 人信息的对象
    person_dict = {}
    for person in person_list:
        face_distance = get_face_distance(face_id, person.face_id)
        person_dict[face_distance] = person
    return person_dict[min(person_dict)], min(person_dict)


def get_face_distance(face_id1, face_id2):
    """获取两张人脸的欧式距离face_id1,face_id2 为128位的列表"""

    # 计算欧式距离
    distance = numpy.linalg.norm(numpy.array(face_id1, dtype=float) - numpy.array(eval(face_id2), dtype=float))

    return distance


# 登录装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('center.views.login', next=request.url))

    return wrapper



