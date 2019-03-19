import flask
from flask import jsonify, session, request, current_app
from flask_cas.cas_urls import create_cas_logout_url

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


@blueprint.route('/logout', methods=['POST', 'GET'])
def logout():
    """用户注销处理"""
    cas_username_session_key = current_app.config['CAS_USERNAME_SESSION_KEY']
    cas_attributes_session_key = current_app.config['CAS_ATTRIBUTES_SESSION_KEY']

    if cas_username_session_key in session:
        del session[cas_username_session_key]

    if cas_attributes_session_key in session:
        del session[cas_attributes_session_key]

    if (current_app.config['CAS_AFTER_LOGOUT'] != None):
        redirect_url = create_cas_logout_url(
            current_app.config['CAS_SERVER'],
            current_app.config['CAS_LOGOUT_ROUTE'],
            current_app.config['CAS_AFTER_LOGOUT'])
    else:
        redirect_url = create_cas_logout_url(
            current_app.config['CAS_SERVER'],
            current_app.config['CAS_LOGOUT_ROUTE'])

    return flask.redirect(redirect_url)
