from flask import (
  Flask, Blueprint, g, render_template, redirect, session, url_for, request
)

from sudoku.auth import login_required
from sudoku.db import get_db

bp = Blueprint('room', __name__, url_prefix='/room')

@bp.route('/create')
def create():
  if request.method == 'POST':
    return
  return render_template('room/create.html')

@bp.route('/join')
def join():
  if request.method == 'POST':
    return
  return render_template('room/join.html')

@bp.route('/show')
def show():
  return render_template('room/show.html')