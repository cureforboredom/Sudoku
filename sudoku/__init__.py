import os

from flask import Flask, url_for, g

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
    
    @app.route('/images/pastime.png')
    def pastime():
        return app.send_static_file("pastime.png")
    
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file("pastime.png")

    @app.before_request
    def get_number_of_solves():
      if g.user:
        d = db.get_db()
        g.solves = d.execute(
          'select count(distinct board_id) as "count" from solved_boards where username = ?',
          (g.user["username"],)
        ).fetchone()['count']

    return app