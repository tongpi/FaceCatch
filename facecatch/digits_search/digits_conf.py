import os
import random
import shutil
import time
import librosa
import requests
import json
import librosa.display
import matplotlib.pyplot as plt

import settings


def get_feature(image, job_id):
    """从digits分类模型获取图像识别的结果"""

    # digits模型分析的地址与job_id
    url = settings.DISCERN_URL

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


def transform_wav(upload_file, job_id):
    os.mkdir('./facecatch/digits_search/cache_file')
    file_name = '%s-%s' % (time.strftime('%Y%m%d-%H%M%S'), str(random.randint(10, 100)))
    with open('./facecatch/digits_search/cache_file/{}.wav'.format(file_name), 'wb') as f:
        f.write(upload_file)
    plt.figure(figsize=(2.56, 2.56))
    x, sr = librosa.load('./facecatch/digits_search/cache_file/{}.wav'.format(file_name))
    librosa.display.waveplot(x, sr=sr)
    plt.savefig('./facecatch/digits_search/cache_file/{}.png'.format(file_name))
    plt.clf()
    with open('./facecatch/digits_search/cache_file/{}.png'.format(file_name), 'rb') as f:
        data = f.read()
    predictions = get_feature(data, job_id=job_id)
    shutil.rmtree('./facecatch/digits_search/cache_file')
    return predictions


def get_digits_models():
    req = requests.get(settings.DISCERN_MODEL_URL)
    try:
        models = json.loads(req.content)['models']
    except:
        return None
    model_dict = dict()
    for model in models:
        model_dict[model['job id']] = model['name']
    return model_dict


def get_first_model():
    req = requests.get(settings.DISCERN_MODEL_URL)
    models = json.loads(req.content)['models']
    return models[-1]['id']
