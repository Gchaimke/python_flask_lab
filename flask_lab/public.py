import os

from urllib.parse import unquote
from flask import Blueprint, render_template, request

from .db import get_where, list_all

from . import const

bp = Blueprint('public', __name__)

unique_not_found_urls = set()

@bp.route('/')
def index():
    return render_template('public/main.html')
