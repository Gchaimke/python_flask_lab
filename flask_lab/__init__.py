from logging.config import dictConfig
import os
from pathlib import Path
from flask import Flask, Response

from . import db
from . import auth
from . import settings
from . import user
from . import public
from . import gallery
from . import brands
from . import products
from . import lab
from . import customer
from .translator import lang


def create_app(test_config=None):
    log_folder = Path(__file__).resolve().parent / 'logs'
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file = log_folder / 'app.log'

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                    "datefmt": "%B %d, %Y %H:%M:%S %Z",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
                "size-rotate": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(log_file),
                    "maxBytes": 1000000,
                    "backupCount": 5,
                    "formatter": "default",
                }
            },
            "root": {"level": "DEBUG", "handlers": ["console", "size-rotate"]},
        }
    )
    # create and configure the app
    app = Flask('flask_lab', instance_relative_config=True,
                template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(gallery.bp)
    app.register_blueprint(public.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(brands.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(lab.bp)
    app.register_blueprint(customer.bp)

    app.add_url_rule('/', endpoint='index')

    app.jinja_env.globals.update(lang=lang)

    return app
