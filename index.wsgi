
import logging
import sys
from flask import Flask


BASE_DIR = '/home/d/denmb/mc88.co.il/public_html'
sys.path.insert(0, BASE_DIR + '/flask_lab')
sys.path.insert(1, BASE_DIR + '/venv/lib/python3.10/site-packages')
activate_this = BASE_DIR + '/venv/bin/activate_this.py'
exec(open(activate_this).read())

import flask_lab

logging.basicConfig(stream=sys.stderr)

app = flask_lab.create_app()
application = app

if __name__ == '__main__':
    app.run()