import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from .const import CLIENTS_DB, LANGUAGE, PRODUCTS_DB, SETTINGS_DB, TICKETS_DB, USERS_DB

# ALTER TABLE user ADD COLUMN language varchar(5) null default 'en'
ADD_COLUMN = "ALTER TABLE {table} ADD COLUMN {column} {column_type}{column_type_param} {null} {default}"


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    setting = {
        'min_role_to_view_board': 1,
        'min_role_to_add': 1,
        'min_role_to_delete': 2,
        'min_role_to_manage_users': 2,
        'min_role_to_manage_settings': 2,
    }
    user = {
        'username': 'admin',
        'view_name': 'admin',
        'role': 2,
        'password': generate_password_hash('admin')
    }
    client = {
        'name': 'Jura',
        'phone': '0541234123',
        'last_ticket_id': 1,
    }
    demo_ticket = {
        'author_id': 1,
        'client_id': '0541234123',
        'pc_login_password': '12345'
    }
    product = {
        'name': 'Product 1',
        'description': 'Product 1 description',
        'price': 100.0,
        'status': 1,
    }
    insert_to_db(table_name=SETTINGS_DB, data=setting)
    insert_to_db(table_name=USERS_DB, data=user)
    insert_to_db(table_name=CLIENTS_DB, data=client)
    insert_to_db(table_name=TICKETS_DB, data=demo_ticket)
    insert_to_db(table_name=PRODUCTS_DB, data=product)
    return '<h1>App init Success!</h1><p> Use user:admin password:admin <a href="/auth/login">Login</a></p>'


@click.command('init-db')
@click.option('--force/--no-force', default=False)
@with_appcontext
def init_db_command(force):
    """Clear the existing data and create new tables."""
    if not get_columns(USERS_DB) or force:
        init_db()
        click.echo(
            'Clear the existing data and create new tables. login with admin:admin in http://localhost:5000/auth/login')
    else:
        click.echo(
            'Table "users" exists, please use "python -m flask init-db --force" parameter to clean start.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_columns(table):
    db = get_db()
    try:
        return [i[1] for i in db.execute(f'PRAGMA table_info({table})')]
    except Exception:
        return False


def add_column(table, column, column_type='varchar', column_type_param='(150)', null='', default=''):
    if not table or not column:
        return None
    db = get_db()
    if columns := get_columns(table):
        if column not in columns:
            if default:
                default = f'default \'{default}\''
            db.execute(
                ADD_COLUMN.format(
                    table=table, column=column, column_type=column_type,
                    column_type_param=column_type_param, null=null, default=default
                )
            )


def insert_to_db(table_name: str, data: dict = None):
    try:
        db = get_db()
        data_values = [i for i in data.values()]
        fields = ', '.join([f'{field}' for field in data.keys()])
        data_map = ', '.join([f'?' for _ in data])
        lastrowid = db.execute(
            f'INSERT INTO {table_name} ({fields}) VALUES ({data_map})', (
                *data_values,)
        ).lastrowid
        db.commit()
        if lastrowid > 0:
            return lastrowid
        return False
    except db.IntegrityError:
        return f"User {data.get('username','')} is already registered."


def update_by_id(table_name: str, id: str = None, data: dict = None, id_key='id'):
    if not id:
        return False
    try:
        db = get_db()
        fields = ','.join([f'{field} = ?' for field in data.keys()])
        data_values = [i for i in data.values()]
        rowcount = db.execute(
            f'UPDATE {table_name} SET {fields} WHERE {id_key} = \'{id}\'', data_values
        ).rowcount
        db.commit()
        if rowcount > 0:
            return True
        return False
    except db.IntegrityError:
        return False


def get_by_id(table_name: str, id, join_with: str = None, join_fields=('id', 'id'), id_key='id'):
    db = get_db()
    if not get_columns(USERS_DB):
        init_db()
    query = f"SELECT * FROM {table_name} a"
    if join_with:
        query += f" JOIN {join_with} b on a.{join_fields[0]} = b.{join_fields[1]}"
    query += f" WHERE a.{id_key} = ?"
    return db.execute(query, (id, )).fetchone()


def get_join(a: str, b: str, join_fields=('id', 'id'), where=None):
    db = get_db()
    query = f"SELECT * FROM {a} a " \
            f"JOIN {b} b on " \
            f"a.{join_fields[0]} = b.{join_fields[1]} "
    if where:
        query += where

    query += f" ORDER BY created DESC"
    return db.execute(query).fetchall()


def get_where(table_name: str, col, val):
    db = get_db()
    return db.execute(
        f"SELECT * FROM {table_name} WHERE {col} = ?", (val,)
    ).fetchone()


def list_all(table_name: str = TICKETS_DB, where: str = ''):
    db = get_db()
    return db.execute(f"SELECT * FROM {table_name} {where}").fetchall()


def delete_by_id(table_name: str = TICKETS_DB, id: int = 0):
    db = get_db()
    db.execute(f'DELETE FROM {table_name} WHERE id = ?', (id,))
    db.commit()


def add_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR DEFAULT '',
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image TEXT DEFAULT '',
            description TEXT DEFAULT '',
            short_description TEXT DEFAULT '',
            price REAL DEFAULT 0.0,
            status INTEGER DEFAULT 0,
            priority INTEGER DEFAULT 0
        )
    ''')
    db.commit()
    product = {
        'name': 'Product 1',
        'description': 'Product 1 description',
        'price': 100.0,
        'status': 1,
    }
    insert_to_db('product', product)
