import os

from urllib.parse import unquote
from flask import Blueprint, render_template, request

from . import const

bp = Blueprint('pablic', __name__)

unique_not_found_urls = set()

@bp.route('/')
def index():
    return render_template('public/main.html')


@bp.route('/power_supplies')
def power_supplies():
    categories = ['dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'apple', 'samsung', 'sony', 'toshiba', 'fujitsu', 'lg',
                  'microsoft', 'xiaomi', 'huawei', 'google']
    categories.sort()
    categories = [category.title() for category in categories]
    return render_template('public/power_supplies.html', categories=categories)


@bp.route('/power_supplies/<category>')
def power_supplies_category(category):
    per_page = 18
    next = None
    not_found = False
    page = request.args.get('page', 0, type=int)  # Default to page 1 if not specified
    if not (products := list(get_category(category))):
        products = list(get_category('19'))
        not_found = True
    products.sort()
    if chunked := chunk_list(products, per_page):
        if page + 1 < len(chunked):
            next = page + 1
        if page > len(chunked) - 1:
            page = len(chunked) - 1
        current_page = chunked[page]
    else:
        current_page = products
    return render_template('public/category.html', products=current_page, next=next, total_pages=len(chunked), not_found=not_found)

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


# @bp.route('/power_supplies/copy')
def copy_matching_images():
    import re
    import shutil
    total = []
    cuted_ps_img = set()
    all_ps_img = set()
    # Define source and destination folders
    source_folder = f'{const.ROOT_PATH}/../wp-content/uploads'

    # Define the pattern for the desired filenames
    all_ps_pattern = r"^.+\d+(W|w).*(?!300.*)\.(jpg|jpeg|JPG|JPEG|png|PNG)$"
    cutted_pattern = r"^.+\d+(W|w).*(-\d+x\d+)\.(jpg|jpeg|JPG|JPEG|png|PNG)$"

    # Compile the regular expression for matching filenames
    all_regex = re.compile(all_ps_pattern)
    cutted_regex = re.compile(cutted_pattern)

    # Iterate through files in the source folder
    images = [f for f in os.listdir(source_folder)]
    for filename in images:
        if all_regex.match(filename):
            all_ps_img.add(filename)
            if cutted_regex.match(filename):
                cuted_ps_img.add(filename)

    unique_ps_images = all_ps_img - cuted_ps_img
    for filename in unique_ps_images:
        source_path = os.path.join(source_folder, filename)
        destination_path = os.path.join(const.POWER_SUPPLIES_FOLDER, filename.lower())
        filename = str(bytes(filename,'utf-8','backslashreplace'),'utf-8')
        msg = f"Copying: {filename}"
        total.append(msg)

        # Copy the file
        shutil.copy(source_path, destination_path)
        print(f"Copied: {filename}")
    return render_template('public/power_supplies.html', msg=total)


def chunk_list(lst, size):
    return [lst[i:i + size] for i in range(0, len(lst), size)]

def get_category(category):
    for filename in (f for f in os.listdir(const.POWER_SUPPLIES_FOLDER) if f.lower().endswith(('.jpg', '.jpeg'))):
        if category.lower() in filename.lower():
            clean_file_name = filename.removesuffix('.jpg').replace('_', ' ').replace('-', ' ').title()
            yield clean_file_name, filename
        