import os
from flask import Flask
from flask_cors import CORS
import logging

from . import db
from . import auth
from . import exercise_checks
from . import admin_actions


def create_app(test_config=None):
    logging.basicConfig(filename='backend.log', filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%m-%y %H:%M:%S')

    app = Flask(__name__)
    CORS(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(exercise_checks.bp)
    app.register_blueprint(admin_actions.bp)

    @app.route('/hello')
    def hello():
        return {'name': 'Orr Sharon', 'about': 'This is me'}

    return app
