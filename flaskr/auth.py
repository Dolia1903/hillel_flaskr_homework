import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        artist_name = request.form['artist_name']
        password = request.form['password']
        db = get_db()
        error = None

        if not artist_name:
            error = 'Artist_name is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO artist (artist_name, password) VALUES (?, ?)",
                    (artist_name, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Artist is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)
        if error == f"Artist is already registered.":
            return redirect(url_for("auth.login"))

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        artist_name = request.form['artist_name']
        password = request.form['password']
        db = get_db()
        error = None
        artist = db.execute(
            'SELECT * FROM artist WHERE artist_name = ?', (artist_name,)
        ).fetchone()

        if artist is None:
            error = 'Incorrect artist_name.'
        elif not check_password_hash(artist['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['artist_name'] = artist['artist_name']
            return redirect(url_for('streaming.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_artist():
    artist_name = session.get('artist_name')

    if artist_name is None:
        g.artist_name = None
    else:
        g.artist_name = get_db().execute(
            'SELECT artist_name FROM artist WHERE artist_name = ?', (artist_name,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.artist_name is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
