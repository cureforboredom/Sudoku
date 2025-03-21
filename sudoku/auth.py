import functools

from flask import (
  Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from sudoku.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')

  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      """
      SELECT *
      FROM users
      WHERE id = ?
      """, (user_id,)
    ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    username = request.form['username'].lower()
    password = request.form['password']
    db = get_db()
    error = None

    if not username:
      error = 'Username is required.'
    elif not password:
      error = 'Password is required.'

    if error is None:
      try:
        board_id = session["board_id"] if session.get("board_id") else None

        db.execute(
          """
          INSERT INTO users
          (username, password, board_id)
          VALUES (?, ?, ?)
          """, (username, generate_password_hash(password), board_id),
        )
        db.commit()
      except db.IntegrityError:
        error = f"User {username} is already registered."
      else:
        return redirect(url_for("auth.login"))

    flash(error)

  return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
  if request.method == 'POST':
    username = request.form['username'].lower()
    password = request.form['password']
    db = get_db()
    error = None
    user = db.execute(
      """
      SELECT *
      FROM users
      WHERE username = ?
      """, (username,)
    ).fetchone()

    if user is None:
      error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
      error = 'Incorrect password.'

    if error is None:
      session['user_id'] = user['id']
      
      room = db.execute(
        """
        SELECT room
        FROM users
        WHERE id = ?
        """, (session['user_id'],)
      ).fetchone()
      
      if room:
        session["room_id"] = room["room"]
      elif session.get('board_id'):
        db.execute(
          """
          UPDATE users
          SET board_id = ?
          WHERE id = ?
          """, (session['board_id'], user['id'])
        )
        db.commit()
      else:
        session['board_id'] = user['board_id']
      return redirect(url_for('index'))

    flash(error)

  return render_template('auth/login.html')


@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))


def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view
