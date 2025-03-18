import requests, json

from flask import (
  Blueprint, flash, g, render_template, request, session, url_for, jsonify
)

from werkzeug.exceptions import abort

from sudoku.auth import login_required
from sudoku.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
  return render_template('main/index.html')

@bp.route('/play')
def play():
  return render_template('main/play.html')