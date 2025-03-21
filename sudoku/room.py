from flask import (
  Flask, Blueprint, g, render_template, redirect, session, url_for, request
)

from sudoku.auth import login_required
from sudoku.db import get_db

bp = Blueprint('room', __name__, url_prefix='/room')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == 'POST':
    db = get_db()
    
    while True:
      try:
        new_room = db.execute(
          """
          INSERT INTO rooms
          (room_key) VALUES (hex(randomblob(3)))
          RETURNING id
          """
        ).fetchone()
        db.commit()
        break
      except:
        pass
    
    db.execute(
      """
      UPDATE users
      SET room = ?
      WHERE id = ?
      """, (new_room["id"], session["user_id"])
    )
    db.commit()
    
    session["room_id"] = new_room["id"]

    return redirect(url_for("room.show"))
  return render_template('room/create.html')

@bp.route('/join', methods=['GET', 'POST'])
@login_required
def join():
  if request.method == 'POST':
    db = get_db()

    room = request.form["room_code"]

    room_id = db.execute(
      """
      SELECT id
      FROM rooms
      WHERE room_key = ?
      """, (room,)
    ).fetchone()["id"]
    
    if room_id:
      db.execute(
        """
        UPDATE users
        SET room = ?
        WHERE id = ?
        """, (room_id, session["user_id"])
      )
      db.commit()
      session["room_id"] = room_id
      return redirect(url_for("room.show"))
    else:
      flash("Room Key Not Valid.")

  return render_template('room/join.html')

@bp.route('/show')
@login_required
def show():
  return render_template('room/show.html')

@bp.route('/leave')
@login_required
def leave():
  db = get_db()
  db.execute(
    """
    UPDATE users
    SET room = 0
    WHERE id = ?
    """, (session["user_id"],)
  )
  db.commit()
  session.pop("room_id")
  session.pop("board_id")
  return redirect(url_for("index"))