import os
from pathlib import Path
from flask import Blueprint, Response, current_app, json, render_template, request

from . import const
from .auth import min_role_required

bp = Blueprint('gallery', __name__, url_prefix='/gallery')


@bp.route('/')
def index():
    return Response(response=json.dumps(get_images()), status=200, mimetype='text/plain')


@bp.route('/upload_image', methods=['POST'])
@min_role_required(min_role_to='delete')
def upload_image():
    current_app.logger.info(request.form)
    return Response(response='Image Uploaded', status=200, mimetype='text/plain')


@bp.route('/upload_from_url', methods=['POST'])
@min_role_required(min_role_to='delete')
def upload_from_url():
    current_app.logger.info(request.form)
    return Response(response='Upload image from url', status=200, mimetype='text/plain')


@bp.route('/delete_image', methods=['POST'])
@min_role_required(min_role_to='delete')
def delete_image():
    current_app.logger.info(request.form)
    return Response(response='Delete image', status=200, mimetype='text/plain')


def get_images(folder=const.POWER_SUPPLIES_FOLDER, formats=('.jpg', '.jpeg', '.png')):
    return {
        file: f'{folder}/{file}'
        for file in os.listdir(f'{const.PUBLIC_IMAGES_FOLDER}/{folder}') if
        file.lower().endswith(formats)
    }
