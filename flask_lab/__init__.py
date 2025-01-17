import os
from flask import Flask

from . import db
from . import auth
from . import settings
from . import user
from . import public
from . import products
from . import lab
from . import customer
from .translator import lang

def create_app(test_config=None):
    # create and configure the app
    app = Flask('flask_lab', instance_relative_config=True, template_folder='templates')
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
    app.register_blueprint(public.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(lab.bp)
    app.register_blueprint(customer.bp)

    app.add_url_rule('/', endpoint='index')

    app.jinja_env.globals.update(lang=lang)

    return app
