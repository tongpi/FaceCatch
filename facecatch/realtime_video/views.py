import flask
import cv2
import numpy

from flask import render_template, Response, jsonify, request

from facecatch.utils import get_image_face, get_same_person, get_person_emotion, FACENET_EMOTION_DICT, get_video_face

blueprint = flask.Blueprint('realtime_video', __name__)

# IMAGE_GLOBAL = None


# class VideoCamera(object):
#     def __init__(self):
#         # 通过opencv获取单个实时视频流
#         self.video = cv2.VideoCapture(0)
#
#     def __del__(self):
#         self.video.release()
#
#     def get_frame(self):
#         success, image = self.video.read()
#         # 用作人脸检测并标记
#         face_image = face_mark(image)
#         try:
#             # 因为opencv读取的图片并非jpeg格式，因此要用motion JPEG模式需要先将图片转码成jpg格式图片
#             ret, jpeg = cv2.imencode('.jpg', face_image)
#         except:
#             self.video.release()
#             return None
#         return jpeg.tobytes(), jpeg
#
#
# def face_mark(image):
#     """用于检测并标记图像中的人脸"""
#     if isinstance(image, numpy.ndarray):
#         # 调用cv2 自带的检测网络
#         detector = cv2.CascadeClassifier('D:\\ProgramData-py3\\Anaconda3\\envs\\FaceCatch\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml')
#         # 将图像转为灰度图
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         # 检测图像中存在的人脸
#         faces = detector.detectMultiScale(gray, 1.3, 5)
#         # 将图像中存在的人脸用方框标记出来
#         for (x, y, w, h) in faces:
#             cv2.rectangle(image, (x, y), (x + w, y + h), (220, 195, 111), 2)
#     return image
#
#
# def image_gen(camera):
#     """用于生成视频帧图片的生成器"""
#     # 此全局变量用来保存用作人脸识别的帧图片
#     global IMAGE_GLOBAL
#     while True:
#         # 捕获异常用于摄像头关闭时重新自动连接
#         try:
#             frame, jpeg = camera.get_frame()
#         except:
#             camera.video = cv2.VideoCapture(0)
#             pass
#         IMAGE_GLOBAL = jpeg
#         if frame:
#             # 使用generator函数输出视频流， 每次请求输出的content类型是image/jpeg
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#
#
# @blueprint.route('/video_feed')
# def video_feed():
#     """用作页面返回视频帧图片的生成器"""
#     return Response(image_gen(VideoCamera()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


@blueprint.route('/recognize', methods=['POST', 'GET'])
def recognize():
    """处理帧图片人脸识别"""
    result_message = {}
    video_image = request.get_data()
    image = str(video_image, 'utf-8').split(',')[1]
    print(image)
    # face_list = get_video_face(image)
    # if len(face_list) >= 1:
    #     person, distance = get_same_person(face_list[0]['faceID'])
    #     emotion = get_person_emotion(face_list[0]['emotion'])[0]
    #     # 定义返回结果字典
    #     if distance < 0.7:
    #         result_message['message'] = person.to_dict()
    #         result_message['emotion'] = FACENET_EMOTION_DICT[emotion]
    #         return jsonify(result_message)
    # result_message['not_message'] = '该人员信息未知。'
    # if IMAGE_GLOBAL is not None:
    #     image = IMAGE_GLOBAL
    #     face_list = get_image_face(image)
    #     if len(face_list) >= 1:
    #         person, distance = get_same_person(face_list[0]['faceID'])
    #         emotion = get_person_emotion(face_list[0]['emotion'])[0]
    #         # 定义返回结果字典
    #         if distance < 0.7:
    #             result_message['message'] = person.to_dict()
    #             result_message['emotion'] = FACENET_EMOTION_DICT[emotion]
    #             return jsonify(result_message)
    # result_message['not_message'] = '该人员信息未知。'
    return jsonify(result_message)


@blueprint.route('/view_video')
def view_video():
    """在线识别跳转"""
    return render_template('realtime_video/search.html')
