import functools, json

from flask import (
        Blueprint, render_template, request, session, url_for
)

from sudoku.db import get_db

bp = Blueprint('play', __name__, url_prefix='/play')

@bp.route('/')
def play():
    db = get_db()
    error = None

    return render_template('play/index.html')
