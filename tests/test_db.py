import sqlite3

import pytest
from flask_lab.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flask_lab.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db', '--force'])
    assert 'Clear the existing data and create new tables' in result.output
    assert Recorder.called