import os

from flask import Flask, url_for, g, session

from sudoku.auth import login_required

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'sudoku.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import api
    app.register_blueprint(api.bp)

    from . import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='index')
    
    from . import room
    app.register_blueprint(room.bp)
    
    @app.route('/images/pastime.png')
    def pastime():
        return app.send_static_file("pastime.png")
    
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file("pastime.png")

    @app.before_request
    def get_g_vars():
      d = db.get_db()
      if session.get("user_id"):
        if not d.execute(
          """
          SELECT *
          FROM users
          """
        ).fetchone():
          session.clear()
        else:
          username = d.execute(
            """
            SELECT username
            FROM users
            WHERE id = ?
            """, (session["user_id"],)
          ).fetchone()['username']
          g.solves = d.execute(
            """
            SELECT COUNT(DISTINCT board_id) AS "count"
            FROM solved_boards
            WHERE username = ?
            """, (username,)
          ).fetchone()['count']
      if session.get("room_id"):
        if not d.execute(
          """
          SELECT *
          FROM users
          """
        ).fetchone():
          session.clear()
        else:
          g.room_key = d.execute(
            """
            SELECT room_key
            FROM rooms
            WHERE id = ?
            """, (session["room_id"],)
          ).fetchone()["room_key"]
    return app