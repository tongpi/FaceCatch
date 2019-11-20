import flask
import base64
import json

from flask import request, render_template, session
from flask.json import jsonify
from flask_cas import login_required

from facecatch.digits_search.forms import UploadForm, UploadSoundForm
from .digits_conf import get_feature, transform_wav, get_digits_models, get_first_model

blueprint = flask.Blueprint('digits', __name__)


@blueprint.route('/digits_search', methods=['GET', 'POST'])
@login_required
def digits_search():
    upload_form = UploadForm()

    if session.get('model_id'):
        digits_model_id = session.get('model_id')
    else:
        digits_model_id = get_first_model()

    if request.method == 'GET':
        return render_template('search/digits_search.html',
                               form=upload_form,
                               base64=base64, )

    upload_file = request.files['file'].read()

    predictions = get_feature(upload_file, digits_model_id)
    if predictions:
        return render_template('search/digits_search.html', form=upload_form, predictions=predictions, image=upload_file, base64=base64)
    else:
        match_result = '此图片未识别，请使用与模型同类型的图片。'

    return render_template(
            'search/digits_search.html',
            form=upload_form,
            image=upload_file,
            match_result=match_result,
            base64=base64)


@blueprint.route('/get_result', methods=['POST'])
@login_required
def get_result():
    if session.get('model_id'):
        digits_model_id = session.get('model_id')
    else:
        digits_model_id = get_first_model()

    upload_file = request.files['file'].read()

    predictions = get_feature(upload_file, digits_model_id)

    return jsonify(predictions)


@blueprint.route('/digits/sounds', methods=["GET", "POST"])
@login_required
def digits_sounds():
    sound_form = UploadSoundForm(request.form)
    if request.method == 'POST':
        upload_file = request.files['file'].read()
        digits_job = request.form.get('job_id')
        predictions = transform_wav(upload_file, digits_job)
        if predictions:
            return render_template('search/digits_sound.html',
                                   form=sound_form,
                                   predictions=predictions,)
        else:
            match_result = '此语音未识别。'

        return render_template(
            'search/digits_sound.html',
            form=sound_form,
            match_result=match_result)

    return render_template('search/digits_sound.html', form=sound_form)


@blueprint.route('/get_models', methods=['POST', 'GET'])
def get_models():
    try:
        session.pop('model_id')
    except:
        pass
    model_dict = get_digits_models()

    if not session.get('model_id'):
        session['model_id'] = get_first_model()

    return jsonify(model_dict)


@blueprint.route('/set_session', methods=['POST', 'GET'])
def set_model_session():
    model_id = json.loads(request.get_data().decode())['model_id']
    session['model_id'] = model_id
    return 'success'
