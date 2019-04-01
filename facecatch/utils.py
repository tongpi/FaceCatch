import base64
import operator
import tempfile
import zipfile

import numpy
import pandas
import requests
import json

from functools import wraps
from flask import session, redirect, url_for, request

import settings
from .models import PersonInfo


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
        image文件夹里的内容为以人员证件号命名的jpg图片。

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
        result_dict['id_card'] = excel_data[1]
        result_dict['description'] = excel_data[2]
        result_dict['image'] = file_zip.open('face/image/{}.png'.format(excel_data[1])).read()
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



