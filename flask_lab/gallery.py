import os
from pathlib import Path
from flask import Blueprint, Response, current_app, json, render_template, request

from flask_lab.utils import chunk_list, get_images

from . import const
from .auth import min_role_required

bp = Blueprint('gallery', __name__, url_prefix='/gallery')


@bp.route('/')
def index():
    page = request.args.get('page', 0, type=int)
    return Response(response=json.dumps(get_images(page=page)), status=200, mimetype='text/plain')


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
