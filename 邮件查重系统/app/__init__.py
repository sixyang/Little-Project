import os
from flask import Flask
from app.models import db
from redis import Redis

redis_conn = Redis(host='127.0.0.1', db=1, port=6379)
base_dir = os.path.dirname(__file__)
attachment_dir = '{0}/../Attachments'.format(base_dir)
temp_dir = '{0}/../Attachments/temp'.format(base_dir)


def register_blueprint(_app):
    from app.views.auth import auth
    from app.views.base import base
    from app.views.email import email
    from app.views.file import file

    _app.register_blueprint(auth)
    _app.register_blueprint(base)
    _app.register_blueprint(email)
    _app.register_blueprint(file)


def create_app():
    _app = Flask(__name__)
    _app.config.from_object('secure')
    _app.config.from_object('settings')
    db.init_app(_app)

    register_blueprint(_app)
    return _app