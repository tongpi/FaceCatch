import requests
import json

import settings


def get_all_models():
    """从digits获取第一个识别模型"""
    url = settings.DISCERN_MODEL_URL
    req = requests.get(url)
    models = json.loads(req.content)['models']
    model_dict = {}
    for model in models:
        model_dict[model['job id']] = model['name']
    return list(model_dict.keys())[0]


def get_feature(image):
    """从digits分类模型获取图像识别的结果"""

    # digits模型分析的地址与job_id
    url = settings.DISCERN_URL
    if settings.DIGITS_JOB_ID:
        job_id = settings.DIGITS_JOB_ID
    else:
        job_id = get_all_models()

    data = {
            'job_id': job_id,
        }
    files = {
        'image_file': image
    }

    # 从digits获取json数据
    req = requests.post(url=url, data=data, files=files)
    if req:
        predictions = json.loads(req.content.decode('utf-8'))['predictions']
        return predictions
    return None
