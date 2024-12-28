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
    unique_file = set()
    # Define source and destination folders
    source_folder = f'{const.ROOT_PATH}/../wp-content/uploads'
    destination_folder = f'{const.ROOT_PATH}/static/img/public/products/matenim'

    # Define the pattern for the desired filenames
    pattern = r"^.+(-|_)?\d+(\.\d+)?(V|v)-\d*(\.\d+)?(A|a)-\d+(W|w)(-|_)?(1|2|3)?\.(jpg|jpeg|JPG|JPEG|png|PNG)$"

    # Ensure the destination folder exists
    # if not os.path.exists(destination_folder):
    #     os.makedirs(destination_folder)

    # Compile the regular expression for matching filenames
    regex = re.compile(pattern)

    # Iterate through files in the source folder
    for filename in os.listdir(source_folder):
        if regex.match(filename):  # Check if the filename matches the pattern
            # unique_file_name = filename.split('W_')[0]
            # if unique_file_name in unique_file:
            #     continue
            # unique_file.add(unique_file_name)
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(destination_folder, filename)
            msg = f"Copying: {filename}"
            total.append(msg)

            # # Copy the file
            # shutil.copy(source_path, destination_path)
            # print(f"Copied: {filename}")
    return render_template('public/matenim.html', msg=total)




