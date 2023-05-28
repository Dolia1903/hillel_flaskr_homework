import random
import sqlite3

import click
from flask import current_app, g

from faker import Faker
from faker_music import MusicProvider
from essential_generators import DocumentGenerator
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def fill_db():
    db = get_db()

    fake = Faker()
    fake.add_provider(MusicProvider)

    for i in range(10):
        title = fake.music_genre()
        db.execute(
            'INSERT INTO genres (title)'
            ' VALUES (?)',
            (title,)
        )
        db.commit()

    for i in range(10):
        name = fake.unique.name()
        db.execute(
            'INSERT INTO artist (artist_name, password)'
            ' VALUES (?,?)',
            (name, generate_password_hash('123456'),)
        )
        db.commit()

    for i in range(30):
        gen = DocumentGenerator()
        title = gen.name()

        random_author = get_db().execute(
            'SELECT artist_name'
            ' FROM artist'
            ' WHERE artist.id = ?',
            (random.randint(1, 10),)
        ).fetchone()

        random_genre_id = random.randint(1, 10)
        random_length = random.randint(90, 300)

        db.execute(
            'INSERT INTO tracks (title, artist, length, genre_id)'
            ' VALUES (?,?,?,?)',
            (title, random_author[0], random_length, random_genre_id,)
        )
        db.commit()


@click.command('fill-db')
def fill_db_command():
    """Clear the existing data and create new tables."""
    fill_db()
    click.echo('Loaded the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(fill_db_command)
