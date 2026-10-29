"""Demo safety, route architecture and a real PostgreSQL locking check."""
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from database_support import DatabaseTestCase
from app.entities import Company, Project, ProjectView, Shortlist, User
from app.extensions import db


class ReadinessTests(DatabaseTestCase):
    def setUp(self):
        with self.app.app_context():
            db.create_all()
        self.runner = self.app.test_cli_runner()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_demo_creates_complete_portfolio_and_hashed_password(self):
        response = self.runner.invoke(args=["seed-demo", "--email", " DEMO@example.com ",
                                            "--password", "demo-password-123"])
        self.assertEqual(response.exit_code, 0, response.output)
        self.assertIn("synthetic demonstration data", response.output)
        with self.app.app_context():
            user = db.session.scalar(db.select(User))
            self.assertEqual(user.email, "demo@example.com")
            self.assertTrue(user.check_password("demo-password-123"))
            self.assertNotEqual(user.password_hash, "demo-password-123")
            for entity, expected in ((User, 1), (Company, 1), (Project, 4), (ProjectView, 15), (Shortlist, 6)):
                self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(entity)), expected)
            for status in ("current", "past"):
                self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Project).filter_by(status=status)), 2)

    def test_demo_refuses_existing_account_without_changing_it(self):
        with self.app.app_context():
            user = User(email="demo.designer@example.com")
            user.set_password("original-password-123")
            db.session.add(user)
            db.session.commit()
        response = self.runner.invoke(args=["seed-demo", "--password", "new-password-123"])
        self.assertNotEqual(response.exit_code, 0)
        self.assertIn("existing data was not changed", response.output)
        with self.app.app_context():
            user = db.session.scalar(db.select(User))
            self.assertTrue(user.check_password("original-password-123"))
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Company)), 0)

    def test_demo_rejects_invalid_input_without_partial_records(self):
        for args in (["--password", "short"], ["--email", "invalid", "--password", "demo-password-123"]):
            response = self.runner.invoke(args=["seed-demo", *args])
            self.assertNotEqual(response.exit_code, 0)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(User)), 0)

    def test_exactly_18_story_controllers_are_wired_to_routes(self):
        actions = ("create", "view", "update", "delete", "search")
        expected = {f"{action}_{subject}_controller" for action in actions
                    for subject in ("company", "current_project", "past_project")}
        expected.update(("auth_controller", "view_project_views_controller", "view_project_shortlists_controller"))
        controller_dir = Path(self.app.root_path) / "controllers"
        self.assertEqual({path.stem for path in controller_dir.glob("*_controller.py")}, expected)
        routed = {handler.__module__.split(".")[-1] for handler in self.app.view_functions.values()}
        self.assertTrue(expected.issubset(routed))
        self.assertEqual(self.app.view_functions["auth.login"].__module__,
                         self.app.view_functions["auth.logout"].__module__)

    def test_postgresql_company_lock_blocks_concurrent_project_insert(self):
        with self.app.app_context():
            if db.engine.dialect.name != "postgresql":
                self.skipTest("Requires PostgreSQL; run scripts/verify_postgres.py")
            user = User(email="lock-test@example.com")
            user.set_password("lock-password-123")
            company = Company(owner=user, name="Lock test")
            db.session.add(company)
            db.session.commit()
            company_id = company.id
            db.session.remove()
            # The deletion controller locks the parent before checking projects.
            # A second connection must not insert a referencing project through it.
            with db.engine.connect() as first, db.engine.connect() as second:
                with first.begin(), second.begin():
                    first.execute(db.select(Company).where(Company.id == company_id).with_for_update())
                    second.execute(text("SET LOCAL lock_timeout = '250ms'"))
                    with self.assertRaises(OperationalError) as caught:
                        second.execute(Project.__table__.insert().values(
                            company_id=company_id, title="Concurrent insert", status="current"))
                    self.assertEqual(caught.exception.orig.sqlstate, "55P03")
                    second.rollback()
