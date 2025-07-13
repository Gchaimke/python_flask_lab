# index.wsgi# This file is used to run the Flask application with a WSGI server.
# It sets up the environment and imports the necessary modules.
# Make sure to adjust the paths according to your project structure.
import logging
import sys
import os

# Set the path to the virtual environment and include it in sys.path
path, _ = os.path.split(os.path.realpath(__file__))
sys.path.insert(0, path)
sys.path.insert(1, f'{path}/venv/lib/python3.10/site-packages')
# Activate the virtual environment
activate_file = f'{path}/venv/bin/activate_this.py'
exec(open(activate_file).read(), dict(__file__=activate_file))


# For testing if flask is installed, uncomment next line
# from flask import Flask
import flask_lab

logging.basicConfig(stream=sys.stderr)

app = flask_lab.create_app()
application = app

if __name__ == '__main__':
    app.run()
