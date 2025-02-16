from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from .auth import min_role_required, login_required
from .db import insert_to_db, update_by_id, list_all, get_by_id, delete_by_id
from .const import CLIENTS_DB, TICKETS_DB

bp = Blueprint('customer', __name__, url_prefix='/customer')


@bp.route('/list')
@min_role_required(min_role_to='manage_customers')
def list():
    customers = list_all(table_name=CLIENTS_DB)
    return render_template("customer/list.html", customers=customers)


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    customer = get_customer(id)
    msg = f"customer updated!"
    redirect_path = 'customer.edit'
    if request.method == 'POST':
        data = {}
        data['name'] = request.form['name']
        data['phone'] = request.form['phone']
        data['email'] = str(request.form['email']).lower()
        data['language'] = request.form['language'] or 'en'

        if update_by_id(table_name=CLIENTS_DB, row_id=id, data=data):
            if customer['phone'] != request.form['phone']:
                update_by_id(
                    table_name=TICKETS_DB,
                    row_id=customer['phone'],
                    data={'client_id': request.form['phone']},
                    id_key='client_id')
            flash(msg, category='info')
            return redirect(url_for(redirect_path, id=id))
        else:
            flash('Can\'t update customer data', category='danger')

    if g.user['role'] >= 1:
        return render_template("customer/edit.html", customer=customer)
    else:
        flash('Permissions error!', category='danger')
        return redirect(url_for('customer.edit', id=id))


@bp.route('/create', methods=('GET', 'POST'))
@min_role_required(min_role_to='manage_customers')
def create():
    if request.method == 'POST':
        data = {}
        data['name'] = request.form['name']
        data['phone'] = request.form['phone']
        data['email'] = str(request.form['email']).lower()
        data['language'] = request.form['language'] or 'en'
        if id := insert_to_db(table_name=CLIENTS_DB, data=data):
            flash(f"customer {data['name']} created!", category='warning')
            return redirect(url_for('customer.edit', id=id))
        else:
            if customer := get_by_id(table_name=CLIENTS_DB, row_id=data['phone'], id_key='phone'):
                return redirect(url_for('customer.edit', id=customer['id']))
            flash('Can\'t insert customer data', category='danger')
    return render_template("customer/create.html", customer={})


@bp.route('/delete/<int:id>', methods=('POST',))
@min_role_required(min_role_to='manage_customers')
def delete(id):
    if g.user['id'] != id:
        customer = get_customer(id)
        delete_by_id(table_name=CLIENTS_DB, row_id=id)
        return redirect(url_for('customer.list'))
    else:
        flash(f"You can't delete your self!", category='danger')
        return redirect(url_for('customer.list'))


def get_customer(id):
    customer = get_by_id(table_name=CLIENTS_DB, row_id=id)
    if customer is None:
        abort(404, f"customer id {id} doesn't exist.")
    return customer
