import flask
from flask import render_template
blueprint = flask.Blueprint(__name__, __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')








