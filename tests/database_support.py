"""SQLite by default; PostgreSQL tests use a new, isolated schema per class."""
import os
import unittest
from uuid import uuid4

from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema, DropSchema

from app import create_app
from app.extensions import db


class DatabaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = {"TESTING": True, "SECRET_KEY": "isolated-test-secret",
                  "SQLALCHEMY_DATABASE_URI": "sqlite://"}
        cls.test_schema = None
        test_url = os.getenv("TEST_DATABASE_URL")
        if test_url:
            if make_url(test_url).drivername != "postgresql+psycopg":
                raise ValueError("TEST_DATABASE_URL must use postgresql+psycopg")
            cls.test_schema = "bce_test_" + uuid4().hex
            config.update(SQLALCHEMY_DATABASE_URI=test_url, SQLALCHEMY_ENGINE_OPTIONS={
                "connect_args": {"connect_timeout": 5},
                "execution_options": {"schema_translate_map": {None: cls.test_schema}},
            })
        cls.app = create_app(config)
        with cls.app.app_context():
            if cls.test_schema:
                with db.engine.begin() as connection:
                    connection.execute(CreateSchema(cls.test_schema))
                cls.addClassCleanup(cls.cleanup_database)
            else:
                @event.listens_for(db.engine, "connect")
                def enable_foreign_keys(connection, record):
                    connection.execute("PRAGMA foreign_keys=ON")
                cls.addClassCleanup(cls.cleanup_database)

    @classmethod
    def cleanup_database(cls):
        with cls.app.app_context():
            db.session.remove()
            if cls.test_schema:
                # Only this class's generated schema is ever removed.
                assert cls.test_schema.startswith("bce_test_") and len(cls.test_schema) == 41
                with db.engine.begin() as connection:
                    connection.execute(DropSchema(cls.test_schema, cascade=True))
            db.engine.dispose()
