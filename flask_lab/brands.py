from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for

from .auth import min_role_required
from .db import delete_by_id, get_by_id, insert_to_db, update_by_id, update_many
from . import const

bp = Blueprint('brands', __name__, url_prefix='/brands')


@bp.route('/delete/<int:brand_id>', methods=['POST'])
@min_role_required(min_role_to='delete')
def delete(brand_id):
    if brand := get_by_id(const.BRANDS_DB, brand_id):
        if brand['id'] == 1:
            flash('Cannot delete Unknown brand', category='error')
            return redirect(url_for('products.power_supplies'))
        update_many(const.PRODUCTS_DB, f'brand = {brand_id}', {'brand': 1})
    delete_by_id(const.BRANDS_DB, brand_id)
    return redirect(url_for('products.power_supplies'))


@bp.route('/create', methods=('GET', 'POST'))
@min_role_required(min_role_to='add')
def create():
    brand = {'id': 0}
    if request.method == 'POST':
        data = {key: value for key, value in request.form.items()}
        brand_id = insert_to_db(table_name=const.BRANDS_DB, data=data)
        current_app.logger.info(f'brand {brand_id=} created.')
        return redirect(url_for('products.power_supplies'))
    return render_template('public/brands/create.html', brand=brand)


@bp.route('/update/<int:brand_id>', methods=('GET', 'POST'))
@min_role_required(min_role_to='add')
def update(brand_id):
    brand = get_by_id(const.BRANDS_DB, brand_id)
    if not brand:
        return redirect(url_for('products.power_supplies'))

    if request.method == 'POST':
        data = {key: value for key, value in request.form.items()}
        update_by_id(const.BRANDS_DB, brand_id, data=data)
        flash('Updated', category='info')
        return redirect(url_for('products.power_supplies'))
    return render_template('public/brands/update.html', brand=brand)
