from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('streaming', __name__)


@bp.route('/')
def index():
    db = get_db()
    tracks = db.execute(
        ' SELECT tr.id, tr.title, artist, length, g.title'
        ' FROM tracks tr '
        ' JOIN genres g on g.id = tr.genre_id'
        ' ORDER BY artist DESC'
    ).fetchall()
    return render_template('streaming/index.html', tracks=tracks)


@bp.route('/create_genre', methods=('GET', 'POST'))
@login_required
def create_genre():
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO genres (title)'
                ' VALUES (?)',
                (title,)
            )
            db.commit()
            return redirect(url_for('streaming.index'))

    return render_template('streaming/create_genre.html')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        length = request.form['length']
        genre_id = request.form['genre_id']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tracks (title, artist, length, genre_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, g.artist_name['artist_name'], length, genre_id)
            )
            db.commit()
            return redirect(url_for('streaming.index'))

    return render_template('streaming/create.html')


def get_track(id, check_author=True):
    track = get_db().execute(
        'SELECT tr.id, title, artist, length, genre_id'
        ' FROM tracks tr JOIN artist art ON art.artist_name = tr.artist'
        ' WHERE tr.id = ?',
        (id,)
    ).fetchone()

    if track is None:
        abort(404, f"Track id {id} doesn't exist.")

    if check_author and track['artist'] != g.artist_name['artist_name']:
        abort(403)

    return track


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    track = get_track(id)

    if request.method == 'POST':
        title = request.form['title']
        length = request.form['length']
        genre_id = request.form['genre_id']
        error = None

        if not title:
            error = 'Title is required.'

        if not length:
            error = 'length is required.'

        if not genre_id:
            error = 'Genre is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tracks SET title = ?, length = ?,  genre_id = ?'
                ' WHERE id = ?',
                (title, length, genre_id, id)
            )
            db.commit()
            return redirect(url_for('streaming.index'))

    return render_template('streaming/update.html', track=track)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_track(id)
    db = get_db()
    db.execute('DELETE FROM tracks WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('streaming.index'))


@bp.route('/names')
def unique_artists():
    db = get_db()
    result = db.execute(
        ' SELECT COUNT(DISTINCT artist)'
        ' FROM tracks '
    ).fetchone()
    return render_template('streaming/unique.html', result=result)


@bp.route('/tracks')
def tracks_number():
    db = get_db()
    result = db.execute(
        ' SELECT COUNT(*) as track'
        ' FROM tracks '
    ).fetchone()
    return render_template('streaming/number.html', result=result)


@bp.route('/tracks/<genre>')
def tracks_genre(genre):
    db = get_db()
    result = db.execute(
        'SELECT COUNT(*)'
        ' FROM tracks as tr'
        ' JOIN genres as gn on tr.genre_id = gn.id'
        ' WHERE gn.title = ?',
        (genre,)
    ).fetchone()
    return render_template('streaming/genre.html', result=result, genre=genre)


@bp.route('/tracks-sec')
def tracks_sec():
    db = get_db()
    tracks = db.execute(
        'SELECT title, length'
        ' FROM tracks as tr'
    ).fetchall()
    return render_template('streaming/seconds.html', tracks=tracks)


@bp.route('/tracks-sec/statistics/')
def tracks_stats():
    db = get_db()
    result = db.execute(
        'SELECT AVG(length), SUM(length)'
        ' FROM tracks as tr'
    ).fetchone()
    return render_template('streaming/statistics.html', result=result)
