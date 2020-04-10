import ssl
from flask import Flask
from flask_cas import CAS
from flask_restful import Api

from facecatch.database import db
import settings
from apscheduler.schedulers.background import BackgroundScheduler

from facecatch.utils import pretreatment_image
from facecatch.search.views import ImageListResource, ImageResource

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

api = Api(webapp)
api.add_resource(ImageListResource, '/api/images_list')
api.add_resource(ImageResource, '/api/image/<unknown_id>')

# webapp.config['SECRET_KEY'] = binascii.hexlify(os.urandom(12)).decode()
# socketio = SocketIO(webapp, async_mode='gevent')


scheduler = BackgroundScheduler()
if settings.PRETREATMENT_IMAGE_PATH:
    scheduler.add_job(pretreatment_image, "cron", hour=settings.PRETREATMENT_HOUR, minute=settings.PRETREATMENT_MINUTE, args=[webapp])
    # scheduler.add_job(pretreatment_image, "interval", minutes=2, args=[webapp])
    scheduler.start()


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


# def guest_decorator(f):
#     from functools import wraps
#     @wraps(f)
#     def home_decorated(*args, **kwargs):
#         this_username = cas.username
#         if this_username is None:
#             return redirect(url_for('search.home'))
#         return f(*args, **kwargs)
#
#     return home_decorated
#
#
# # for endpoint in endpoints:
# for endpoint, function in webapp.view_functions.items():
#     if endpoint not in ['search.home', 'cas.login', 'static', 'cas.logout']:
#         webapp.view_functions[endpoint] = guest_decorator(function)


if __name__ == '__main__':
    webapp.run(host='0.0.0.0',
               port=5000,
               ssl_context=(
                    "local_ssl/cert.pem",
                    "local_ssl/key.pem")
               )
