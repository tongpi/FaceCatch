import flask
import base64

from flask import request, render_template
from flask_cas import login_required

from facecatch.digits_search.forms import UploadForm, UploadSoundForm
from .digits_conf import get_feature, transform_wav

blueprint = flask.Blueprint('digits', __name__)


@blueprint.route('/digits_search', methods=['GET', 'POST'])
@login_required
def digits_search():
    upload_form = UploadForm()
    if request.method == 'GET':
        return render_template('search/digits_search.html',
                               form=upload_form,
                               base64=base64, )

    upload_file = request.files['file'].read()
    digits_job = request.form.get('job_id')
    predictions = get_feature(upload_file, digits_job)
    if predictions:
        return render_template('search/digits_search.html', form=upload_form, predictions=predictions, image=upload_file, base64=base64)
    else:
        match_result = '该人员信息未知。'

    return render_template(
            'search/digits_search.html',
            form=upload_form,
            image=upload_file,
            match_result=match_result,
            base64=base64)


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

