"""
系统相关设置
"""
import os


FLASK_SECRET_KEY = 'face_catch'

SQLALCHEMY_DATABASE_URI = os.environ.get("FACECATCH_DATABASE_URL", "postgresql:///postgres")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)

# DIGITS地址的配置
DISCERN_IP = os.environ.get('DISCERN_ADDRESS', '192.168.15.100:50333')
DISCERN_URL = 'http://{ip}/models/images/classification/classify_one.json'.format(ip=DISCERN_IP)
DIGITS_JOB_ID = os.environ.get('DIGITS_JOB_ID', '20190312-031331-71ad')




