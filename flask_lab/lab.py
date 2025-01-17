from sqlite3 import OperationalError
import sqlite3
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import min_role_required
from .db import add_db, init_db, insert_to_db, update_by_id, delete_by_id, get_by_id, get_join
from . import const

bp = Blueprint('lab', __name__, url_prefix='/lab')


@bp.before_app_request
def set_const():
    g.roles = const.ROLES
    g.app_name = const.APP_NAME
    g.app_ver = const.APP_VERSION
    g.priorities = const.PIORITY
    g.status = const.STATUS
    g.language = const.LANGUAGE
    g.pc_manufacturers = const.PC_MANUFACTURERS
    g.pc_kind = const.PC_KIND
    g.colors = const.COLORS
    g.with_power_supply = {0: 'no', 1: 'yes'}


@bp.route('/init')
def init():
    try:
        get_by_id(table_name=const.USERS_DB, id=1)
        return 'App init, user exists'
    except OperationalError:
        return init_db()


@bp.route('/')
@min_role_required(min_role_to='view_board')
def index():
    add_db()
    settings = get_by_id(table_name=const.SETTINGS_DB, id=1)
    refresh = settings['refresh'] or 60
    tickets = get_join(
        a=const.TICKETS_DB,
        b=const.CLIENTS_DB,
        join_fields=('client_id', 'phone'))
    return render_template('lab/list.html', tickets=tickets, refresh=refresh)


@bp.route('/board')
@min_role_required(min_role_to='view_board')
def index_done():
    settings = get_by_id(table_name=const.SETTINGS_DB, id=1)
    refresh = settings['refresh'] or 60
    tickets = get_join(
        a=const.TICKETS_DB,
        b=const.CLIENTS_DB,
        join_fields=('client_id', 'phone'))
    return render_template('lab/board.html', tickets=tickets, refresh=refresh)


@bp.route('/create', methods=('GET', 'POST'))
@min_role_required(min_role_to='add')
def create():
    ticket = {'id': 0}
    if request.method == 'POST':
        error = None
        data = {key: value for key, value in request.form.items() if key in const.TICKET_EDIT_FILEDS}
        data.update({'author_id': g.user['id'], 'client_id': request.form['client_id']})

        if not request.form['client_id']:
            error = 'client id is required.'

        if error is not None:
            flash(error, category='danger')
        else:
            id = insert_to_db(table_name=const.TICKETS_DB, data=data)
            insert_to_db(table_name=const.CLIENTS_DB, data={
                         'phone': request.form['client_id'], 'name': request.form['name'], 'last_ticket_id': id})
            current_app.logger.info(f'Ticket {id=} created.')
            return redirect(url_for('lab.update', id=id))

    return render_template('lab/create.html', ticket=ticket)


@bp.route('/<int:id>/done', methods=('GET', 'POST'))
@min_role_required(min_role_to='view_board')
def done(id):
    update_by_id(table_name=const.TICKETS_DB, id=id, data={'status': 1})
    flash('Updated', category='info')
    return redirect(url_for('index'))


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@min_role_required(min_role_to='add')
def update(id):
    ticket: sqlite3.Row = get_ticket(id)
    if request.method == 'POST':
        error = None
        data = {key: value for key, value in request.form.items(
        ) if key in const.TICKET_EDIT_FILEDS}
        data.update({'author_id': g.user['id']})
        if error is not None:
            flash(error, category='danger')
        else:
            update_by_id(table_name=const.TICKETS_DB, id=id, data=data)
            flash('Updated', category='info')
            return redirect(url_for('lab.update', id=id))
    return render_template('lab/update.html', ticket=ticket)


@bp.route('/<int:id>/delete', methods=('POST',))
@min_role_required(min_role_to='delete')
def delete(id):
    get_ticket(id)
    delete_by_id(table_name=const.TICKETS_DB, id=id)
    current_app.logger.info(f'Ticket {id=} deleted.')
    return redirect(url_for('index'))


def get_ticket(id, check_author=True):
    ticket = get_by_id(
        table_name=const.TICKETS_DB,
        id=id,
        join_with=const.CLIENTS_DB,
        join_fields=('client_id', 'phone')
    )
    if ticket is None:
        abort(404, f"ticket id {id} doesn't exist.")

    if g.user['role'] > 1:
        return ticket

    if check_author and ticket['author_id'] != g.user['id']:
        abort(403)

    return ticket
