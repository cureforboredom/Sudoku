import requests, json, logging

from hashlib import sha1

from flask import (
  Blueprint, request, session, url_for, jsonify
)

from sudoku.auth import login_required
from sudoku.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')

logging.basicConfig(
  encoding="utf-8",
  format="{asctime} - {levelname} - {message}",
  style="{",
  datefmt="%Y-%m-%d %H:%M",
  level=logging.DEBUG,
)

def load_board():
  logging.debug("starting: load board. Get db.")
  db = get_db()
  logging.debug("Get db result: %s", json.dumps(db))
  return json.loads(db.execute(
    "SELECT board FROM boards WHERE id = ?",
    (session["board_id"],)
  ).fetchone()[0])


@bp.route('/new_board', methods=(['GET','POST']))
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
  
@bp.route('/get_board')
def get_board():
  hash = request.args.get('hash')
  db = get_db()

  board = load_board()

  new_hash = sha1(str(board).encode("utf-8")).hexdigest()

  if not hash == new_hash:
    return {"board": board, "hash": new_hash}
  else:
    return '', 204
  
@bp.route('/modify_board', methods=['POST'])
def modify_board():
  db = get_db()

  r = request.get_json()
  y = r[0] // 9
  x = r[0] % 9
  v = r[1]

  board = load_board()
  
  if board[y][x][1]:
    board[y][x][0] = v
  
    db.execute(
      "UPDATE boards SET board = ? WHERE id = ?",
      (json.dumps(board), session["board_id"])
    )
    db.commit()

  return '', 204