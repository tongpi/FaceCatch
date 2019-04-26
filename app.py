import ssl

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_cas import CAS

from facecatch.database import db
import settings


webapp = Flask(__name__, template_folder="facecatch/templates", static_folder="facecatch/static")
cas = CAS(webapp)


ssl._create_default_https_context = ssl._create_unverified_context
webapp.config['CAS_SERVER'] = settings.CAS_SERVER
webapp.config['CAS_AFTER_LOGIN'] = settings.CAS_AFTER_LOGIN
webapp.config['CAS_VALIDATE_ROUTE'] = settings.CAS_VALIDATE_ROUTE
webapp.config['CAS_LOGOUT_ROUTE'] = settings.CAS_LOGOUT_ROUTE
webapp.config['CAS_AFTER_LOGOUT'] = settings.CAS_AFTER_LOGOUT


webapp.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
webapp.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
webapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(webapp)


@webapp.before_first_request
def create_db():
    db.create_all()


from facecatch import views
webapp.register_blueprint(views.blueprint)
from facecatch.staff import views
webapp.register_blueprint(views.blueprint)
from facecatch.search import views
webapp.register_blueprint(views.blueprint)
from facecatch.realtime_video import views
webapp.register_blueprint(views.blueprint)
from facecatch.expression import views
webapp.register_blueprint(views.blueprint)
from facecatch.digits_search import views
webapp.register_blueprint(views.blueprint)

CSRFProtect(webapp)


if __name__ == '__main__':
    webapp.run(host='0.0.0.0',
               port=5000,
               ssl_context=(
                    "local_ssl/cert.pem",
                    "local_ssl/key.pem")
               )
