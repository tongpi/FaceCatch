import flask
from flask import Response, jsonify, session, request
from facecatch.utils import get_all_models
import json


blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/get_models', methods=['POST', 'GET'])
def get_models():
    """获取模型列表，将默认模型存储至session"""
    model_dict = get_all_models()

    if not session.get('model_id'):
        session['model_id'] = list(model_dict.keys())[0]

    return jsonify(model_dict)


@blueprint.route('/set_session', methods=['POST', 'GET'])
def set_model_session():
    """跟随模型下拉框设置系统默认模型"""
    model_id = json.loads(request.get_data().decode())['model_id']
    session['model_id'] = model_id
    return 'success'
