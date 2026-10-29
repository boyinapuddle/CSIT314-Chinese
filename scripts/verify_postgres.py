"""Run all HTTP/CLI tests in temporary PostgreSQL schemas; preserve public data."""
import os
from pathlib import Path
import sys
import unittest

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")


def main():
    raw = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw:
        print("Set DATABASE_URL in .env or TEST_DATABASE_URL in the environment.")
        return 1
    try:
        url = make_url(raw)
        if url.drivername != "postgresql+psycopg":
            print("Use a postgresql+psycopg connection URL.")
            return 1
        engine = create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect() as connection:
            print("PostgreSQL connected. Version:", connection.scalar(text("SHOW server_version")))
            expected = {"users", "companies", "projects", "project_views", "shortlists"}
            missing = expected - set(inspect(connection).get_table_names(schema="public"))
            print("Missing app tables in public:", ", ".join(sorted(missing)) or "none")
        engine.dispose()
    except Exception as exc:
        original = getattr(exc, "orig", exc)
        # Do not print a URL, password or full exception containing connection data.
        print("PostgreSQL check failed:", type(original).__name__)
        print("Check the service, port, credentials and database. Local PostgreSQL 18 was observed on port 5433.")
        return 1
    os.environ["TEST_DATABASE_URL"] = raw
    print("Tests create and remove only generated bce_test_* schemas; public tables are untouched.", flush=True)
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
