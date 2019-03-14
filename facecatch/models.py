from app import webapp
from app import db


@webapp.before_first_request
def create_db():
    db.create_all()
