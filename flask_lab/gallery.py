import os
from pathlib import Path
from flask import Blueprint, Response, current_app, json, render_template, request

from flask_lab.utils import get_images

from . import const
from .auth import min_role_required
import requests

bp = Blueprint('gallery', __name__, url_prefix='/gallery')


@bp.route('/')
def index():
    page = request.args.get('page', 0, type=int)
    return Response(response=json.dumps(get_images(page=page)), status=200, mimetype='text/plain')


@bp.route('/upload_image', methods=['POST'])
@min_role_required(min_role_to='delete')
def upload_image():
    image = request.files.get('image')
    if not image:
        return Response(response='Error: No image provided', status=400, mimetype='text/plain')

    # Check MIME type
    if image.mimetype not in ['image/jpeg', 'image/png']:
        return Response(response='Error: Invalid image type', status=400, mimetype='text/plain')

    # Save the image
    image_name = request.form.get('image_name') or image.filename or 'image.jpg'
    # Determine the file extension based on MIME type
    extension = '.jpg' if image.mimetype == 'image/jpeg' else '.png'
    image_name = f"{Path(image_name).stem}{extension}".lower()
    image_path = Path(const.PUBLIC_IMAGES_FOLDER) / const.POWER_SUPPLIES_FOLDER / image_name
    image.save(image_path)
    current_app.logger.info(f"Image saved to {image_path}")
    return Response(response=f'{const.POWER_SUPPLIES_FOLDER}/{image_name}', status=200, mimetype='text/plain')
    


@bp.route('/upload_from_url', methods=['POST'])
@min_role_required(min_role_to='delete')
def upload_from_url():
    image_url = request.form.get('image_url')
    if not image_url:
        return Response(response='Error: No image URL provided', status=400, mimetype='text/plain')

    # Download the image
    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except requests.RequestException as e:
        current_app.logger.error(f"Error downloading image: {e}")
        return Response(response='Error: downloading image', status=400, mimetype='text/plain')

    # Check MIME type
    if response.headers['Content-Type'] not in ['image/jpeg', 'image/png']:
        return Response(response='Error: Invalid image type', status=400, mimetype='text/plain')
    # Save the image
    image_name = request.form.get('image_name') or os.path.basename(image_url)
    # Determine the file extension based on MIME type
    extension = '.jpg' if response.headers['Content-Type'] == 'image/jpeg' else '.png'
    image_name = f"{Path(image_name).stem}{extension}".lower()
    image_path = Path(const.PUBLIC_IMAGES_FOLDER) / const.POWER_SUPPLIES_FOLDER / image_name
    try:
        with open(image_path, 'wb') as f:
            f.write(response.content)
    except Exception:
        current_app.logger.exception(f"Error saving image to {image_path}")
        return Response(response='Error saving image', status=500, mimetype='text/plain')

    current_app.logger.info(f"Image saved to {image_path=}")
    return Response(response=f'{const.POWER_SUPPLIES_FOLDER}/{image_name}', status=200, mimetype='text/plain')


@bp.route('/delete_image', methods=['POST'])
@min_role_required(min_role_to='delete')
def delete_image():
    image = request.form.get('image')
    if not image:
        return Response(response='Error: No image provided', status=400, mimetype='text/plain')

    image_path = Path(const.PUBLIC_IMAGES_FOLDER) / image
    if not image_path.exists():
        return Response(response=f'Error: Image not found {image_path=}', status=404, mimetype='text/plain')

    try:
        image_path.unlink()
    except Exception:
        current_app.logger.exception(f"Error deleting image {image_path}")
        return Response(response='Error deleting image', status=500, mimetype='text/plain')
    current_app.logger.info(f'Image deleted: {image_path=}')
    return Response(response='Image deleted successfuly!', status=200, mimetype='text/plain')
