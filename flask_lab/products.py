import os
import ipaddress
from urllib.parse import unquote
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for, abort

from flask_lab.gallery import get_images
from flask_lab.utils import chunk_list

from .auth import min_role_required
from .db import delete_by_id, get_by_id, get_by_id_as_dict, get_where, insert_to_db, list_all, update_by_id
from . import const

bp = Blueprint('products', __name__, url_prefix='/products')

unique_not_found_urls = set()


@bp.before_request
def block_ip_ranges():
    client_ip = request.remote_addr
    if client_ip:
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            blocked_ips = []
            with open(const.BLOCKED_IPS_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '/' in line:
                            blocked_ips.append(ipaddress.ip_network(line, strict=False))
                        else:
                            blocked_ips.append(ipaddress.ip_address(line))
            for blocked_range in blocked_ips:
                if client_ip_obj in blocked_range:
                    current_app.logger.warning(f"Blocked access from {client_ip}")
                    abort(403)  # Forbidden
        except ValueError as e:
            current_app.logger.error(f"Invalid IP address {client_ip}: {e}")
            pass

@bp.route('/')
def index():
    return render_template('public/main.html')


@bp.route('/power_supplies')
def power_supplies():
    filter_active = 'WHERE status = 1' if not g.user else ''
    categories = list_all(const.BRANDS_DB, where=filter_active)
    return render_template('public/products/power_supplies.html', categories=categories)


@bp.route('/power_supplies/<category>')
def power_supplies_category(category):
    if not (products := list(get_category(category))):
        products = list(get_category('Unknown'))
        not_found = True

    per_page = 18
    next = None
    not_found = False
    # Default to page 1 if not specified
    page = request.args.get('page', 0, type=int)
    if chunked := chunk_list(products, per_page):
        if page + 1 < len(chunked):
            next = page + 1
        if page > len(chunked) - 1:
            page = len(chunked) - 1
        current_page = chunked[page]
    else:
        current_page = products
    return render_template('public/products/category.html', products=current_page, category=category, next=next, total_pages=len(chunked), not_found=not_found)


@bp.route('/product/<int:product_id>')
def product(product_id):
    product = get_by_id_as_dict(const.PRODUCTS_DB, product_id, join_fields=(
        'brand', 'id'), join_with=const.BRANDS_DB)
    if not product:
        return redirect(url_for('products.power_supplies'))
    return render_template('public/products/product.html', product=product)


@bp.route('/delete/<int:product_id>', methods=['POST'])
@min_role_required(min_role_to='delete')
def delete(product_id):
    delete_by_id(const.PRODUCTS_DB, product_id)
    return redirect(url_for('products.power_supplies'))


@bp.route('/create', methods=('GET', 'POST'))
@min_role_required(min_role_to='add')
def create():
    product = {'id': 0, 'name': 'new product', 'description': '', 'brand': '', 'image': 'PSnotebookMC.jpg', 'price': 0, 'status': 1}
    brands = list_all(const.BRANDS_DB, where='WHERE status = 1')
    if request.method == 'POST':
        error = None
        data = {key: value for key, value in request.form.items(
        ) if key in const.PRODUCT_UPDATE_FIELDS}
        if error is not None:
            flash(error, category='danger')
        else:
            product_id = insert_to_db(table_name=const.PRODUCTS_DB, data=data)
            current_app.logger.info(f'Product {product_id=} created.')
            return redirect(url_for('products.product', product_id=product_id))
    return render_template('public/products/create.html', product=product, brands=brands)


@bp.route('/update/<int:product_id>', methods=('GET', 'POST'))
@min_role_required(min_role_to='add')
def update(product_id):
    product = get_by_id(const.PRODUCTS_DB, product_id)
    if not product:
        return redirect(url_for('products.power_supplies'))
    brands = list_all(const.BRANDS_DB, where='WHERE status = 1')
    if request.method == 'POST':
        error = None
        data = {key: value for key, value in request.form.items(
        ) if key in const.PRODUCT_UPDATE_FIELDS}
        if error is not None:
            flash(error, category='danger')
        else:
            update_by_id(table_name=const.PRODUCTS_DB,
                         row_id=product_id, data=data)
            flash('Updated', category='info')
            return redirect(url_for('products.product', product_id=product['id']))
    return render_template('public/products/update.html', product=product, brands=brands)


# Catch-all route for non-existing pages
@bp.app_errorhandler(404)
def page_not_found(e):
    # Log the requested URL (optional)
    if not request.url in unique_not_found_urls:
        current_app.logger.warning(f"NOT FOUND: {request.url} from {request.remote_addr=}")
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
        destination_path = os.path.join(
            const.PUBLIC_IMAGES_FOLDER, const.POWER_SUPPLIES_FOLDER, filename.lower())
        filename = str(bytes(filename, 'utf-8', 'backslashreplace'), 'utf-8')
        msg = f"Copying: {filename}"
        total.append(msg)

        # Copy the file
        shutil.copy(source_path, destination_path)
        print(f"Copied: {filename}")
    return render_template('public/products/power_supplies.html', msg=total)


def get_category(category):
    if brand := get_where(const.BRANDS_DB, 'name', category):
        filter_active = 'AND status = 1' if not g.user else ''
        if cutegory_products := list_all(const.PRODUCTS_DB, where=f"WHERE brand = {brand['id']} {filter_active}"):
            for product in cutegory_products:
                yield product
