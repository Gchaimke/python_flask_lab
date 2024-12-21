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

@bp.route('/')
def index():
    return render_template('public/main.html')

