from flask import Blueprint, Response, current_app, render_template, request

from .auth import min_role_required

bp = Blueprint('public', __name__)


@bp.route('/')
def index():
    return render_template('public/main.html')


@bp.route('/robots.txt')
def noindex():
    r = Response(response="User-Agent: *\nDisallow: *.html\nAllow: /",
                 status=200, mimetype="text/plain")
    r.headers["Content-Type"] = "text/plain; charset=utf-8"
    return r
