"""
系统相关设置
"""
import os


FACECATCH_URL = "https://recognize.lhqw.gfdx.mtn:5000/"


FLASK_SECRET_KEY = 'face_catch'

SQLALCHEMY_DATABASE_URI = os.environ.get("FACECATCH_DATABASE_URL", "postgresql:///")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)

# DIGITS地址的配置
DISCERN_IP = os.environ.get('DISCERN_ADDRESS', '')
DISCERN_URL = 'http://{ip}/models/images/classification/classify_one.json'.format(ip=DISCERN_IP)
DISCERN_MODEL_URL = 'http://{ip}/model.json'.format(ip=DISCERN_IP)
DIGITS_JOB_ID = os.environ.get('DIGITS_JOB_ID', '')

#FACENET
FACENET_IP = os.environ.get('FACENET_ADDRESS', '')
FACENET_URL = 'http://{ip}/user'.format(ip=FACENET_IP)

# CAS
CAS_SERVER = os.environ.get('CAS_SERVER', "https://cas.lhqw.gfdx.mtn")
CAS_AFTER_LOGIN = os.environ.get('CAS_AFTER_LOGIN', "/")
CAS_VALIDATE_ROUTE = os.environ.get('CAS_VALIDATE_ROUTE', "/serviceValidate")
CAS_LOGOUT_ROUTE = os.environ.get('CAS_LOGOUT_ROUTE', "/logout")
CAS_AFTER_LOGOUT = os.environ.get('CAS_AFTER_LOGOUT', FACECATCH_URL)

# 预处理图片的路径
PRETREATMENT_IMAGE_PATH = os.environ.get('PRETREATMENT_IMAGE_PATH', "")
PRETREATMENT_TIME = os.environ.get('PRETREATMENT_TIME', "22:00")
PRETREATMENT_HOUR = int(PRETREATMENT_TIME.split(":")[0])
PRETREATMENT_MINUTE = int(PRETREATMENT_TIME.split(":")[1])

# 人员信息图片存储位置（重要！）
PERSON_STORAGE_ADDRESS = os.environ.get('PERSON_STORAGE_ADDRESS',
                                        os.path.abspath(os.path.dirname(__file__))
                                        .split('FaceCatch')[0] + 'FaceCatch/facecatch/static/person_images')