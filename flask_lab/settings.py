from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from .const import LANGUAGE, SETTINGS_DB, USERS_DB

from .auth import min_role_required
from .db import add_column, update_by_id, get_by_id

bp = Blueprint('settings', __name__)


@bp.route('/settings', methods=('GET', 'POST'))
@min_role_required(min_role_to='manage_settings')
def index():
    settings = get_by_id(table_name=SETTINGS_DB, id=1)
    if request.method == 'POST':
        error = None
        refresh = request.form['refresh']
        data = {
            # 'langauge': request.form['langauge'],
            'refresh': refresh if int(refresh) > 5 else 5,
            'min_role_to_view_board': request.form['min_role_to_view_board'],
            'min_role_to_add': request.form['min_role_to_add'],
            'min_role_to_delete': request.form['min_role_to_delete'],
            'min_role_to_manage_users': request.form['min_role_to_manage_users'],
            'min_role_to_manage_settings': request.form['min_role_to_manage_settings'],
        }
        if error is not None:
            flash(error, category='danger')
        else:
            update_by_id(table_name=SETTINGS_DB, id=1, data=data)
            flash('Update success!', category='info')
            return redirect(url_for('settings.index'))
    return render_template('settings/edit.html', settings=settings)


@bp.route('/update_db', methods=('GET', 'POST'))
@min_role_required(min_role_to='manage_settings')
def update_db():
    column = 'language'
    if add_column(USERS_DB, column, default=LANGUAGE):
        return f"{column=} is added."
    return f"Error adding {column=}, this column exists."