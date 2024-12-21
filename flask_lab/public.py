from sqlite3 import OperationalError
import sqlite3
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import min_role_required
from .db import init_db, insert_to_db, update_by_id, delete_by_id, get_by_id, get_join
from . import const

bp = Blueprint('pablic', __name__)


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


@bp.route('/')
def index():
    return render_template('public/main.html')

