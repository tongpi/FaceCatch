import flask
import base64

from flask import request, render_template
from flask_cas import login_required

from facecatch.digits_search.forms import UploadForm
from .digits_conf import get_feature


blueprint = flask.Blueprint('digits_search', __name__)


@blueprint.route('/digits_search', methods=['GET','POST'])
@login_required
def digits_search():
    upload_form = UploadForm()
    if request.method == 'GET':
        return render_template('search/digits_search.html',
                               form=upload_form,
                               base64=base64, )

    upload_file = request.files['file'].read()
    predictions = get_feature(upload_file)
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
