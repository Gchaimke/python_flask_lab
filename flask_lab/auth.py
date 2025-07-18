import functools
import ipaddress
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app, abort
from .db import get_by_id, insert_to_db, get_where
from .const import LANGUAGE, SETTINGS_DB, USERS_DB, BLOCKED_IPS_FILE, WHITELIST_IPS_FILE

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_request
def block_ip_ranges():
    client_ip = request.remote_addr
    block_ips = _load_ips(BLOCKED_IPS_FILE)
    whitelist_ips = _load_ips(WHITELIST_IPS_FILE)
    if client_ip:

        # Check if the client IP is in the blocked IP ranges
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            if client_ip_obj in whitelist_ips:
                return
            for blocked_range in block_ips:
                if isinstance(blocked_range, ipaddress.IPv4Network) or \
                        isinstance(blocked_range, ipaddress.IPv6Network):
                    if client_ip_obj in blocked_range:
                        current_app.logger.warning(
                            f"Blocked access from {client_ip} in range {blocked_range}")
                        abort(500)
                elif isinstance(blocked_range, ipaddress.IPv4Address) or \
                        isinstance(blocked_range, ipaddress.IPv6Address):
                    # If it's a single IP address, check if it matches
                    if client_ip_obj == blocked_range:
                        current_app.logger.warning(
                            f"Blocked access from {client_ip}")
                        abort(500)
        except ValueError as e:
            current_app.logger.error(f"Invalid IP address {client_ip}: {e}")
            pass
        # Block access to PHP and WordPress URLs
        if _block_php_and_wp_urls(client_ip):
            abort(500)


def _block_php_and_wp_urls(client_ip):
    """Block access to PHP and WordPress URLs."""
    blocked_wp_urls = ['wp-admin', 'wp-login', 'wp-json', 'wp-content']
    if any(url in request.url for url in blocked_wp_urls) or request.url.endswith('.php'):
        _block_ip(client_ip)
        return True
    return False


def _load_ips(file):
    ips = set()
    try:
        with open(file, 'r') as f:
            for line in f:
                try:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '/' in line:
                            ips.add(ipaddress.ip_network(line, strict=False))
                        else:
                            ips.add(ipaddress.ip_address(line))
                except ValueError as e:
                    current_app.logger.error(
                        f"Invalid IP address or network {line}: {e}")
    except FileNotFoundError:
        if file not in {BLOCKED_IPS_FILE, WHITELIST_IPS_FILE}:
            current_app.logger.warning(f"Blocked IPs file {file} not found, creating it.")
            with open(file, 'w') as f:
                pass
        current_app.logger.error(f"Blocked IPs file {file} not found.")
    return ips


def _block_ip(ip):
    """Block a specific IP address."""
    if len(ip) > 50 or ' ' in ip or '\n' in ip:
        current_app.logger.warning(
            f"Blocked IP {ip} is too long and was not added.")
        return
    try:
        ipaddress.ip_address(ip)  # Validate IP address format
    except ValueError:
        current_app.logger.error(f"Invalid IP address {ip} format.")
        return
    with open(BLOCKED_IPS_FILE, 'a') as f:
        f.write(f"{ip}\n")
    current_app.logger.warning(f"Blocked IP {ip} added to {BLOCKED_IPS_FILE}")


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
                current_app.logger.info(
                    f'New user registered {username} from {request.remote_addr}')
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
            current_app.logger.info(
                f'{username=} logged in from {request.remote_addr}.')
            return redirect(url_for('lab.index'))

        flash('Incorrect password or user not exists!', category='danger')
        current_app.logger.error(
            f'{request.remote_addr=} | Login Alert {username=} {password=}')
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
                    flash(f"You don\'t have permissions for this!",
                          category='danger')
                    return redirect(url_for('lab.index'))
                return redirect(url_for('auth.login'))

            return view(**kwargs)
        return wrapped_view
    return decorator
