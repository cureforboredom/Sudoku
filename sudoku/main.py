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
  db = get_db()
  
  if session.get("room_id"):
    board_id = db.execute(
      """
      SELECT id
      FROM boards
      WHERE room = ?
      ORDER BY id
      DESC
      LIMIT 1
      """, (session["room_id"],)
    ).fetchone()
    if board_id:
      session["board_id"] = board_id["id"]
      db.execute(
        """
        UPDATE users
        SET board_id = ?
        WHERE id = ?
        """, (session["board_id"], session["user_id"])
      )
      db.commit()
    else:
      new_board()
  else:
    if not session.get('board_id'):
      new_board()
    elif not db.execute(
      """
      SELECT *
      FROM boards
      """
      ).fetchone():
      new_board()
    else:
      r = db.execute(
        """
        SELECT id
        FROM boards
        WHERE id = ?
        """, (session.get('board_id'),)
      ).fetchone()
      if not r:
        new_board()
      elif r['id'] != session.get('board_id'):
        new_board()
  return render_template('main/play.html')