from sqlite3 import OperationalError
import sqlite3
import ipaddress
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import min_role_required
from .db import init_db, insert_to_db, update_by_id, delete_by_id, get_by_id, get_join
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
                    abort(403)  # Forbidden
        except ValueError as e:
            current_app.logger.error(f"Invalid IP address {client_ip}: {e}")
            pass

@bp.route('/init')
def init():
    try:
        get_by_id(table_name=const.USERS_DB, row_id=1)
        return 'App init, user exists'
    except OperationalError:
        return init_db()


@bp.route('/')
@min_role_required(min_role_to='view_board')
def index():
    settings = get_by_id(table_name=const.SETTINGS_DB, row_id=1)
    refresh = settings['refresh'] or 60
    tickets = get_join(
        a=const.TICKETS_DB,
        b=const.CLIENTS_DB,
        join_fields=('client_id', 'phone'))
    return render_template('lab/list.html', tickets=tickets, refresh=refresh)


@bp.route('/board')
@min_role_required(min_role_to='view_board')
def index_done():
    settings = get_by_id(table_name=const.SETTINGS_DB, row_id=1)
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
        data = {key: value for key, value in request.form.items() if key in const.TICKET_EDIT_FIELDS}
        data.update({'author_id': g.user['id'], 'client_id': request.form['client_id']})

        if not request.form['client_id']:
            error = 'client id is required.'

        if error is not None:
            flash(error, category='danger')
        else:
            ticket_id = insert_to_db(table_name=const.TICKETS_DB, data=data)
            insert_to_db(table_name=const.CLIENTS_DB, data={
                         'phone': request.form['client_id'], 'name': request.form['name'], 'last_ticket_id': ticket_id})
            current_app.logger.info(f'Ticket {ticket_id=} created.')
            return redirect(url_for('lab.update', ticket_id=ticket_id))

    return render_template('lab/create.html', ticket=ticket)


@bp.route('/done/<int:ticket_id>', methods=('GET', 'POST'))
@min_role_required(min_role_to='view_board')
def done(ticket_id):
    update_by_id(table_name=const.TICKETS_DB, row_id=ticket_id, data={'status': 1})
    flash('Updated', category='info')
    return redirect(url_for('lab.index'))


@bp.route('/update/<int:ticket_id>', methods=('GET', 'POST'))
@min_role_required(min_role_to='add')
def update(ticket_id):
    ticket: sqlite3.Row = get_ticket(ticket_id)
    if not ticket:
        return redirect(url_for('lab.index'))

    if request.method == 'POST':
        error = None
        data = {key: value for key, value in request.form.items(
        ) if key in const.TICKET_EDIT_FIELDS}
        data.update({'author_id': g.user['id']})
        if error is not None:
            flash(error, category='danger')
        else:
            update_by_id(table_name=const.TICKETS_DB, row_id=ticket_id, data=data)
            flash('Updated', category='info')
            return redirect(url_for('lab.update', ticket_id=ticket_id))
    return render_template('lab/update.html', ticket=ticket)


@bp.route('/delete/<int:ticket_id>', methods=('POST',))
@min_role_required(min_role_to='delete')
def delete(ticket_id):
    get_ticket(ticket_id)
    delete_by_id(table_name=const.TICKETS_DB, row_id=ticket_id)
    return redirect(url_for('lab.index'))


def get_ticket(ticket_id, check_author=True):
    ticket = get_by_id(
        table_name=const.TICKETS_DB,
        row_id=ticket_id,
        join_with=const.CLIENTS_DB,
        join_fields=('client_id', 'phone')
    )
    if ticket is None:
        abort(404, f"ticket id {ticket_id} doesn't exist.")

    if g.user['role'] > 1:
        return ticket

    if check_author and ticket['author_id'] != g.user['id']:
        abort(403)

    return ticket
