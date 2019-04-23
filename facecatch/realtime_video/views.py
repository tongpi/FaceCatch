import flask

from flask import render_template, jsonify, request

from facecatch.utils import get_same_person, get_person_emotion, FACENET_EMOTION_DICT, get_image_face

blueprint = flask.Blueprint('realtime_video', __name__)


@blueprint.route('/recognize', methods=['POST', 'GET'])
def recognize():
    """处理帧图片人脸识别"""
    result_message = {}
    video_image = request.get_data()
    image = str(video_image, 'utf-8').split(',')[1]
    face_list = get_image_face(image, 'base64')
    if len(face_list) >= 1:
        person, distance = get_same_person(face_list[0]['faceID'])
        emotion = get_person_emotion(face_list[0]['emotion'])[0]
        # 定义返回结果字典
        if distance < 0.7:
            result_message['message'] = person.to_dict()
            result_message['emotion'] = FACENET_EMOTION_DICT[emotion]
            return jsonify(result_message)
    result_message['not_message'] = '该人员信息未知。'

    return jsonify(result_message)


@blueprint.route('/view_video')
def view_video():
    """在线识别跳转"""
    return render_template('realtime_video/search.html')
