import requests, json, logging

from hashlib import sha1

from flask import (
  Blueprint, g, request, session, url_for, jsonify
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
  db = get_db()
  return json.loads(db.execute(
    "SELECT board FROM boards WHERE id = ?",
    (session["board_id"],)
  ).fetchone()[0])

def check_cell(x, y, v):
  board = load_board()

  if v in [board[y][i][0] for i in range(9)]:
    bad_row = list(range(y * 9, y * 9 + 9))
    return {"bad row": bad_row}

  if v in [board[i][x][0] for i in range(9)]:
    bad_column = list(range(x, x + 81, 9))
    return {"bad column": bad_column}
  
  if v in [
    cell[0] for row in board[
      y // 3 * 3: y // 3 * 3 + 3
    ] for cell in row[
      x // 3 * 3: x // 3 * 3 + 3
    ]
  ]:
    bad_square = []
    for i in range(3):
      start = ((y//3*3)+i)*9+(x//3*3)
      bad_square+=list(range(start, start+3))
    return {"bad square": bad_square}
  
  return "valid"

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

  board = load_board()

  new_hash = sha1(str(board).encode("utf-8")).hexdigest()

  if not hash == new_hash:
    return {"board": board, "hash": new_hash}
  else:
    return '', 204
  
@bp.route('/modify_board', methods=['POST'])
def modify_board():
  r = request.get_json()
  y = r[0] // 9
  x = r[0] % 9
  v = int(r[1])

  board = load_board()
  
  if board[y][x][1]: #editable
    if v: #nonzero
      valid = check_cell(x, y, v)
      if valid != "valid":
        return valid

    board[y][x][0] = v

    db = get_db()

    db.execute(
      "UPDATE boards SET board = ? WHERE id = ?",
      (json.dumps(board), session["board_id"])
    )
    db.commit()

  return {"valid": "valid"}

@bp.route('/check_board')
def check_board():
  valid = "True"
  
  board = load_board()

  # check that all rows are valid
  if sum([
    len(set([
      cell[0] for cell in row
    ])) for row in board
  ]) != 81:
    valid = "False"
  
  # check that all columns are valid
  if sum([
    len(set([
      row[i][0] for row in board
    ])) for i in range(9)
  ]) != 81:
    valid = "False"
    
  # check that all squares are valid
  for i in range(0, 9, 3):
    for j in range(0, 9, 3):
      pairs = board[i][j: j+3]
      pairs.extend(board[i+1][j: j+3])
      pairs.extend(board[i+2][j: j+3])
      if not len(set([pair[0] for pair in pairs])) == 9:
        valid = "False"

  if valid == "True" and session.get('user_id'):
    db = get_db()
    db.execute(
      'INSERT INTO solved_boards (username, board_id) VALUES (?, ?)',
      (g.user['username'], session['board_id'])
    )
    db.commit()

  return valid

@bp.route('/debug_set_valid_board')
def debug_set_valid_board():
  board = [
    [[1, False],[2, False],[3, False],[4, False],[5, False],[6, False],[7, False],[8, False],[9, False]],
    [[4, False],[5, False],[6, False],[7, False],[8, False],[9, False],[1, False],[2, False],[3, False]],
    [[7, False],[8, False],[9, False],[1, False],[2, False],[3, False],[4, False],[5, False],[6, False]],
    [[2, False],[3, False],[4, False],[5, False],[6, False],[7, False],[8, False],[9, False],[1, False]],
    [[5, False],[6, False],[7, False],[8, False],[9, False],[1, False],[2, False],[3, False],[4, False]],
    [[8, False],[9, False],[1, False],[2, False],[3, False],[4, False],[5, False],[6, False],[7, False]],
    [[3, False],[4, False],[5, False],[6, False],[7, False],[8, False],[9, False],[1, False],[2, False]],
    [[6, False],[7, False],[8, False],[9, False],[1, False],[2, False],[3, False],[4, False],[5, False]],
    [[9, False],[1, False],[2, False],[3, False],[4, False],[5, False],[6, False],[7, False],[8, False]],
  ]

  db = get_db()

  db.execute(
    "UPDATE boards SET board = ? WHERE id = ?",
    (json.dumps(board), session["board_id"])
  )
  db.commit()
  
  return '', 200