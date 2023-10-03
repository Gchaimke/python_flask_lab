from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import abort
from .auth import min_role_required, login_required
from .db import insert_to_db, update_by_id, list_all, get_by_id, delete_by_id
from .const import ROLES, USERS_DB

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/list')
@min_role_required(min_role_to='manage_users')
def list():
    users = list_all(table_name=USERS_DB)
    return render_template("user/list.html", users=users)


@bp.route('/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit(id):
    user = get_user(id)
    msg = f"User updated!"
    redirect_path = 'lab.index'
    if request.method == 'POST':
        data = {}
        data['view_name'] = request.form['view_name']
        data['email'] = str(request.form['email']).lower()
        data['language'] = request.form['language'] or 'en'
        password = request.form['password']
        if password:
            data['password'] = generate_password_hash(password)

        if g.user['role'] == 2:
            data['username'] = str(request.form['username']).lower()
            data['role'] = request.form['role']
            data['status'] = request.form['status']
            msg = f"User {data['username']} updated!"
            redirect_path = 'user.list'

        if update_by_id(table_name=USERS_DB, id=id, data=data):
            flash(msg, category='info')
            return redirect(url_for(redirect_path))
        else:
            flash('Can\t update user data', category='danger')
    if g.user['id'] == id or g.user['role'] == 2:
        return render_template("user/edit.html", user=user)
    else:
        flash('Pernissions error!', category='danger')
        return redirect(url_for('index'))


@bp.route('/create', methods=('GET', 'POST'))
@min_role_required(min_role_to='manage_users')
def create():
    if request.method == 'POST':
        data = {}
        data['username'] = str(request.form['username']).lower()
        data['view_name'] = request.form['view_name'] or ''
        data['email'] = str(request.form['email']).lower() or ''
        data['password'] = generate_password_hash(request.form['password'])
        data['role'] = request.form['role']
        data['status'] = request.form['status'] or 0
        data['language'] = request.form['language'] or 'en'
        if insert_to_db(table_name=USERS_DB, data=data):
            flash(f"User {data['username']} creted!", category='warning')
            return redirect(url_for('user.list'))
        else:
            flash('Can\t insert user data', category='danger')
    return render_template("user/create.html", user={})


@bp.route('/delete/<int:id>', methods=('POST',))
@min_role_required(min_role_to='manage_users')
def delete(id):
    if g.user['id'] != id:
        user = get_user(id)
        delete_by_id(table_name=USERS_DB, id=id)
        flash(f"User {user['username']} deleted", category='warning')
        return redirect(url_for('user.list'))
    else:
        flash(f"You can't delete your self!", category='danger')
        return redirect(url_for('user.list'))


def get_user(id):
    user = get_by_id(table_name=USERS_DB, id=id)
    if user is None:
        abort(404, f"User id {id} doesn't exist.")
    return user
