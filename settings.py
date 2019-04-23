"""
系统相关设置
"""
import os


FACECATCH_URL = "https://recognize.lhqw.gfdx.mtn:5000/"


FLASK_SECRET_KEY = 'face_catch'

SQLALCHEMY_DATABASE_URI = os.environ.get("FACECATCH_DATABASE_URL", "postgresql://postgres@192.168.1.143/face")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)

# DIGITS地址的配置
DISCERN_IP = os.environ.get('DISCERN_ADDRESS', '192.168.15.100:50333')
DISCERN_URL = 'http://{ip}/models/images/classification/classify_one.json'.format(ip=DISCERN_IP)
DISCERN_MODEL_URL = 'http://{ip}/model.json'.format(ip=DISCERN_IP)
DIGITS_JOB_ID = os.environ.get('DIGITS_JOB_ID', '20190312-031331-71ad')

#FACENET
FACENET_IP = os.environ.get('FACENET_ADDRESS', '192.168.15.100:50555')
FACENET_URL = 'http://{ip}/user'.format(ip=FACENET_IP)

# CAS
CAS_SERVER = os.environ.get('CAS_SERVER', "https://cas.lhqw.gfdx.mtn")
CAS_AFTER_LOGIN = os.environ.get('CAS_AFTER_LOGIN', "/")
CAS_VALIDATE_ROUTE = os.environ.get('CAS_VALIDATE_ROUTE', "/serviceValidate")
CAS_LOGOUT_ROUTE = os.environ.get('CAS_LOGOUT_ROUTE', "/logout")
CAS_AFTER_LOGOUT = os.environ.get('CAS_AFTER_LOGOUT', FACECATCH_URL)



