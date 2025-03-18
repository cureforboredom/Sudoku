import requests, json

from flask import (
  Blueprint, request, session, url_for, jsonify
)

from sudoku.auth import login_required
from sudoku.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/new_board')
def new_board():
  db = get_db()
  r = requests.get("https://sudoku-api.vercel.app/api/dosuku")
  if r.status_code == 200:
    b = r.json()["newboard"]["grids"][0]["value"]
    board = []
    for old_row in b:
      board.append([(cell, False) if cell else (cell, True) for cell in old_row])
            
    db.execute(
      "INSERT INTO boards (board) VALUES (?) RETURNING id",
      (json.dumps(board),),
    )
    db.commit()
    
    row = db.execute("select last_insert_rowid()").fetchone()
    
    (session["board_id"], ) = row if row else None
    if session.get('user_id'):
      db.execute(
        "UPDATE users SET board_id = ? WHERE id = ?",
        (session["board_id"], session["user_id"])
      )
      db.commit()
    return '', 204