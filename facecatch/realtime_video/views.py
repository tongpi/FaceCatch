import flask
import cv2

from flask import render_template, Response, session, jsonify

from facecatch.models import PersonInfo
from facecatch.utils import get_feature


blueprint = flask.Blueprint(__name__, __name__)


class VideoCamera(object):
    def __init__(self):
        # 通过opencv获取实时视频流
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        # 用作人脸检测并标记
        face_image = face_mark(image)
        try:
            # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
            ret, jpeg = cv2.imencode('.jpg', face_image)
        except:
            self.video.release()
            return None
        return jpeg.tobytes(), jpeg


def face_mark(image):
    if image != None:
        """用于检测并标记图像中的人脸"""
        # 调用cv2 自带的检测网络
        detector = cv2.CascadeClassifier(r'D:\ProgramData-py3\Anaconda3\envs\FaceCatch\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml')
        # 将图像转为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 检测图像中存在的人脸
        faces = detector.detectMultiScale(gray, 1.3, 5)
        # 将图像中存在的人脸用方框标记出来
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (220, 195, 111), 2)
        # 将标记后的图像还原为彩色图显示
        cv2.imshow('frame', image)
    return image


def image_gen(camera):
    global IMAGE_B
    while True:
        frame, jpeg = camera.get_frame()
        # 此全局变量用来保存用作人脸识别的帧图片
        IMAGE_B = jpeg
        if frame:
            # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@blueprint.route('/video_feed')
def video_feed():
    """用作页面返回视频帧图片的生成器"""
    return Response(image_gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@blueprint.route('/recognize', methods=['POST', 'GET'])
def recognize():
    """处理帧图片人脸识别"""
    image = IMAGE_B
    model_id = session['model_id']
    # 调用digits获取人脸图片的特征及相似度
    face_feature, similarity = get_feature(image, model_id)
    # 定义返回结果字典
    result_message = {}
    if similarity > 40:
        # 从基础人员库中获取人员信息
        person = PersonInfo.query.filter(PersonInfo.face_feature == face_feature, PersonInfo.model_id == model_id).first()
        if person:
            result_message['message'] = person.to_dict()
            return jsonify(result_message)
    result_message['not_message'] = '该人员信息未知。'

    return jsonify(result_message)


@blueprint.route('/view_video')
def view_video():
    """在线识别跳转"""
    return render_template('realtime_video/search.html')
