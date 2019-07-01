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

from PIL import Image
from flask import session, redirect, url_for, request, jsonify

import settings
from facecatch.database import db
from .models import PersonInfo, ImageInfo, UnknownPersonInfo

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
CREATED_PERSON_IMAGES_PATH = os.path.abspath(os.path.dirname(__file__)).split('FaceCatch')[0] + 'FaceCatch/facecatch/static/person_images'
PERSON_IMAGES_PATH = '/static/person_images'


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
    try:
        face_list = json.loads(req.content.decode('utf-8'))['data']
    except:
        return []
    if face_list is not None:
        return face_list
    return []


def get_same_person(face_id, model=None):
    """获取库中相同的人的信息face_id 为列表，返回距离最小的人信息及人脸距离"""

    if model == "unknown":
        # 获取未知人脸库中的所有人的信息
        person_list = UnknownPersonInfo.query.filter().all()
    else:
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
    try:
        excel_file = file_zip.open('{}face.xlsx'.format(file_zip.namelist()[0]))
    except KeyError:
        excel_file = file_zip.open('{}face.xls'.format(file_zip.namelist()[0]))
    except Exception:
        return None

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
        write_image(result_dict['image'], result_dict['id_card'])
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


def get_all_files(path, suffix1, suffix2):
    """获取指定目录下所有指定文件"""
    return [os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files if file.endswith(suffix1) or file.endswith(suffix2)]


def get_all_image(path):
    """获取指定目录下所有JPG，PNG图片"""
    image_path = []
    for root, dirs, files in os.walk(path):
        image_path += glob.glob(root + '/*.JPG')
        image_path += glob.glob(root + '/*.PNG')
    # jpg_path = glob.glob(path + "/*.JPG")
    # png_path = glob.glob(path + "/*.PNG")
    # return jpg_path + png_path
    return image_path


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
        unknown_image_path = []

        if image_path:
            # 获取所有图片的路径
            file_list = get_all_files(image_path, '.jpg', '.png')
            file_list = file_list if file_list else get_all_image(image_path)

            for file in file_list:
                # 获取文件创建时间
                file_create_time = get_file_create_time(file)
                if max_create_time and file_create_time <= max_create_time:
                    continue
                with open(file, 'rb') as f:
                    file_b64 = base64.b64encode(f.read()).decode("utf-8")
                    face_list = get_image_face(file_b64, "true")
                    for face_data in face_list:
                        face_id = face_data['faceID']
                        person, distance = get_same_person(face_id)
                        if distance < 0.9:
                            image_info = ImageInfo(
                                label=person.name,
                                create_time=file_create_time,
                                image_path=file,
                            )
                            db.session.add(image_info)
                            db.session.commit()
                        else:
                            unknown_image_path.append(file)

        # 读取未识别的图片
        for unknown_image in set(unknown_image_path):
            file_create_time = get_file_create_time(unknown_image)
            with open(unknown_image, 'rb') as f:
                file_b64 = base64.b64encode(f.read()).decode("utf-8")
                face_list = get_image_face(file_b64, "true")
                for face_data in face_list:
                    face_id = face_data['faceID']
                    # 从未知人员库进行比对
                    person, distance = get_same_person(face_id, "unknown")
                    if distance < 0.9:
                        # 存储至图片库
                        image_info = ImageInfo(
                            unknown_id=person.id,
                            label=person.name,
                            create_time=file_create_time,
                            image_path=unknown_image,
                        )
                        db.session.add(image_info)
                        db.session.commit()
                    else:
                        try:
                            max_unknown_id = UnknownPersonInfo.query.order_by(db.desc("id")).first().id
                        except AttributeError:
                            max_unknown_id = 0

                        unknown_info = UnknownPersonInfo(
                            name="未知人员{}".format(max_unknown_id + 1),
                            face_id=str(face_id),
                            image_path=unknown_image,
                        )
                        db.session.add(unknown_info)
                        db.session.commit()

    # print("执行完毕，时间： " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
    return None


def get_same_image(label):
    """从预处理图片库中返回匹配的图片信息"""
    image_info_list = ImageInfo.query.filter(ImageInfo.label == label).all()

    # TODO(dzh): 此处注释为标准JSON返回格式，因配合调用方，临时使用字符串返回值
    # json_data = {"image_data": []}
    # for image_info in image_info_list:
    #     json_data["image_data"].append(
    #         {"unknown_id": image_info.unknown_id,
    #          "path": image_info.image_path})
    # return jsonify(json_data)

    data_str = ''
    try:
        for image_info in image_info_list:
            data_str += "{unknown_id:%s, path:%s}@#!@#!" % (image_info.unknown_id, image_info.image_path)
    except:
        return None
    return data_str


def save_feature_image(face_list):
    """根据facenet返回的人脸位置，在原图中裁剪出人脸图片"""
    bbox_list = []
    for face_data in face_list:
        bbox = face_data["bbox"]
        bbox_tuple = (bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"])
        bbox_list.append(bbox_tuple)
    img = Image.open(r"C:\Users\dengzihao\Desktop\dzh\桌面文件\_DSC1103.JPG", )
    for index, bbox_tuple in enumerate(bbox_list):
        region = img.crop(bbox_tuple)
        region.save(r"C:\Users\dengzihao\Desktop\dzh\人脸提取/{}.jpg".format(index))
    return None


def write_image(image, id_card):
    with open(CREATED_PERSON_IMAGES_PATH + '/{}.jpg'.format(id_card), 'wb') as f:
        f.write(image)
        return None
