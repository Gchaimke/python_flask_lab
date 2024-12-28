from sqlite3 import OperationalError
import sqlite3
from urllib.parse import unquote
from flask import (
    Blueprint, app, current_app, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import min_role_required
from .db import init_db, insert_to_db, update_by_id, delete_by_id, get_by_id, get_join
from . import const

unique_not_found_urls = set()
bp = Blueprint('pablic', __name__)

@bp.route('/')
def index():
    return render_template('public/main.html')


# Catch-all route for non-existing pages
@bp.app_errorhandler(404)
def page_not_found(e):
    # Log the requested URL (optional)
    if not request.url in unique_not_found_urls:
        print(f"NOT FOUND: {request.url}")
    unique_not_found_urls.add(request.url)
    clean_url = unquote(request.path)
    if last_slash := clean_url.split('/'):
        last_slash = last_slash[-1]
    # Respond with a custom message or redirect
    return render_template('public/main.html', requested_url=clean_url, last_slash=last_slash)

