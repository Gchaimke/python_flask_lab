import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from .db import get_by_id, insert_to_db, get_where
from .const import LANGUAGE, ROLES, SETTINGS_DB, USERS_DB

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        if not get_by_id(table_name=USERS_DB, row_id=1):
            role = 2
        else:
            role = 0
        username = str(request.form['username']).lower()[0:20]
        data = {
            'username': username,
            'view_name': str(request.form['view_name'])[0:30],
            'email': str(request.form['email']).lower()[0:30],
            'role': role,
            'language': LANGUAGE,
            'password': generate_password_hash(request.form['password'])
        }
        error = None

        if not username:
            error = 'Username is required.'
        elif not request.form['password']:
            error = 'Password is required.'

        if error is None:
            if id := insert_to_db(table_name=USERS_DB, data=data):
                flash(f'Hello {username}', category='info')
                session['user_id'] = id
                current_app.logger.info(f'New user registered {username}')
                return redirect(url_for("index"))

        if error:
            flash(error, category='danger')

    return render_template('auth/register.html', user={})


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = str(request.form['username']).lower()[0:10]
        password = request.form['password']
        user = get_where(table_name=USERS_DB, col='username', val=username)
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            current_app.logger.info(f'{username=} loged in.')
            return redirect(url_for('lab.index'))

        flash('Incorrect password or user not exists!', category='danger')
        current_app.logger.error(f'{request.remote_addr=} | Login Alert {username=} {password=}')
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_by_id(table_name=USERS_DB, row_id=user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def min_role_required(min_role_to):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            settings = get_by_id(table_name=SETTINGS_DB, row_id=1)
            if g.user and g.user['role'] == 2:
                return view(**kwargs)

            if not g.user and settings[f'min_role_to_{min_role_to}'] == -1:
                return view(**kwargs)

            if not g.user or g.user['role'] < settings[f'min_role_to_{min_role_to}']:
                if g.user:
                    flash(f"You don\'t have permissions for this!", category='danger')
                    return redirect(url_for('lab.index'))
                return redirect(url_for('auth.login'))

            return view(**kwargs)
        return wrapped_view
    return decorator
