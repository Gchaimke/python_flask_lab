
import logging
import sys
import os
from flask import Flask


path, _ = os.path.split(os.path.realpath(__file__))
sys.path.insert(0, path)
sys.path.insert(1, f'{path}/venv/lib/python3.10/site-packages')
exec(open(f'{path}/venv/bin/activate_this.py').read())

import flask_lab

logging.basicConfig(stream=sys.stderr)

app = flask_lab.create_app()
application = app

if __name__ == '__main__':
    app.run()