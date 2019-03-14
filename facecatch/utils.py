from functools import wraps

import requests
import json

from flask import session, redirect, url_for, request

import settings


def get_feature(image):
    """从digits分类模型获取图像识别的结果"""

    # digits模型分析的地址与job_id
    url = settings.DISCERN_URL
    data = {
        'job_id': settings.DIGITS_JOB_ID,
    }
    files = {
        'image_file': image
    }

    # 从digits获取json数据
    req = requests.post(url=url, data=data, files=files)
    predictions = json.loads(req.content.decode('utf-8'))['predictions']

    face_feature = str(predictions[0][0])
    similarity = float(predictions[0][1])
    return face_feature, similarity


# 登录装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('center.views.login', next=request.url))

    return wrapper
