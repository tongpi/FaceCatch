import flask
from flask import render_template
from flask_cas import login_required

# from app import cas


blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET', 'POST'])
# @login_required
def home():
    # print(cas.username)
    return render_template('base.html')








