import requests, json

from flask import (
  Blueprint, flash, g, render_template, request, session, url_for, jsonify, redirect
)

from werkzeug.exceptions import abort

from sudoku.auth import login_required
from sudoku.db import get_db
from sudoku.api import new_board

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
  return render_template('main/index.html')

@bp.route('/play')
def play():
  db = get_db();
  if not session.get('board_id'):
    new_board()
  elif session.get('board_id') != db.execute(
    "SELECT id FROM boards WHERE id = ?",
    (session.get('board_id'),)
  ).fetchone():
    print("fixed it")
    new_board()
  return render_template('main/play.html')