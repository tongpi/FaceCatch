import flask
from flask import jsonify, session, request, current_app, render_template
from flask_cas import login_required
from flask_cas.cas_urls import create_cas_logout_url

blueprint = flask.Blueprint('facecatch', __name__)


@blueprint.route('/logout', methods=['POST', 'GET'])
@login_required
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


@blueprint.route('/error', methods=['GET'])
@login_required
def error():
    data = request.args['data']
    # data = "人脸识别服务连接失败，请检服务的运行状态以及地址的配置！"
    return render_template("error.html", data=data)
