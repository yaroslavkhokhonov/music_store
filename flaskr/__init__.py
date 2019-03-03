from flask import Flask
from flask_restful import Api

from flaskr.models import db, Song
from flaskr.resources import init_resources
from flaskr.settings import DATABASE_NAME


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(SECRET_KEY='dev')

    if test_config is None:
        app.config['MONGOALCHEMY_DATABASE'] = DATABASE_NAME
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    api = Api(app)
    init_resources(api)
    return app
