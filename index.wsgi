
import logging
import sys
from flask import Flask

from flask_lab.const import ROOT_PATH


# BASE_DIR = '/home/d/denmb/mc88.co.il/public_html'
sys.path.insert(0, ROOT_PATH + '/flask_lab')
sys.path.insert(1, ROOT_PATH + '/venv/lib/python3.10/site-packages')
activate_this = ROOT_PATH + '/venv/bin/activate_this.py'
exec(open(activate_this).read())

import flask_lab

logging.basicConfig(stream=sys.stderr)

app = flask_lab.create_app()
application = app

if __name__ == '__main__':
    app.run()