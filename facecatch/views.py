import flask
from flask import Response, jsonify, session, request
from facecatch.utils import get_all_models
import json
# from app import cas

blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/get_models', methods=['POST', 'GET'])
def get_models():
    model_dict = get_all_models()
    model_list = list(model_dict.keys())

    if not session.get('model_id'):
        session['model_id'] = model_list[0]

    return jsonify(model_dict)


@blueprint.route('/set_session', methods=['POST', 'GET'])
def set_model_session():
    model_id = json.loads(request.get_data().decode())['model_id']
    print(model_id)
    print(session.get('model_id'))
    session['model_id'] = model_id
    print(session.get('model_id'))
    return 'success'
