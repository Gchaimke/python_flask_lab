from urllib.parse import unquote
from flask import Blueprint, render_template, request

from . import const

unique_not_found_urls = set()
bp = Blueprint('pablic', __name__)

@bp.route('/')
def index():
    return render_template('public/main.html')


@bp.route('/matenim')
def matenim():
    return render_template('public/matenim.html')


# Catch-all route for non-existing pages
@bp.app_errorhandler(404)
def page_not_found(e):
    # Log the requested URL (optional)
    if not request.url in unique_not_found_urls:
        print(f"NOT FOUND: {request.url}")
    unique_not_found_urls.add(request.url)
    clean_url = unquote(request.path)
    if last_slash := clean_url.split('/'):
        last_slash = last_slash[-1]
    # Respond with a custom message or redirect
    return render_template('public/main.html', requested_url=clean_url, last_slash=last_slash)

@bp.route('/matenim/copy')
def copy_matching_images():
    import os
    import re
    import shutil
    total = []
    cuted_ps_img = set()
    all_ps_img = set()
    # Define source and destination folders
    source_folder = f'{const.ROOT_PATH}/../wp-content/uploads'
    destination_folder = f'{const.ROOT_PATH}/static/img/public/products/matenim'

    # Define the pattern for the desired filenames
    all_ps_pattern = r"^.+\d+(W|w).*\.(jpg|jpeg|JPG|JPEG|png|PNG)$"
    cutted_pattern = r"^.+\d+(W|w).*(-\d+x\d+)\.(jpg|jpeg|JPG|JPEG|png|PNG)$"

    # Ensure the destination folder exists
    # if not os.path.exists(destination_folder):
    #     os.makedirs(destination_folder)

    # Compile the regular expression for matching filenames
    all_regex = re.compile(all_ps_pattern)
    cutted_regex = re.compile(cutted_pattern)

    # Iterate through files in the source folder
    for filename in os.listdir(source_folder):
        if all_regex.match(filename):
            all_ps_img.add(filename)
            if cutted_regex.match(filename):
                cuted_ps_img.add(filename)

    unique_ps_images = all_ps_img - cuted_ps_img
    for filename in unique_ps_images:
        source_path = os.path.join(source_folder, filename)
        destination_path = os.path.join(destination_folder, filename)
        filename = str(bytes(filename,'utf-8','backslashreplace'),'utf-8')
        msg = f"Copying: {filename}"
        total.append(msg)

    # # Copy the file
    # shutil.copy(source_path, destination_path)
    # print(f"Copied: {filename}")
    return render_template('public/matenim.html', msg=total)
