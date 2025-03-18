from flask import (
        Blueprint, flash, g, render_template, request, session, url_for
)

from werkzeug.exceptions import abort

from sudoku.auth import login_required
from sudoku.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    error = None

    return render_template('main/index.html')
