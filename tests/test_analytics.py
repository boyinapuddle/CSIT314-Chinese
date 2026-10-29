"""Owner-only analytics and minimal public engagement through HTTP."""
import re
import unittest
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from database_support import DatabaseTestCase
from app.entities import Company, Project, ProjectView, Shortlist, User
from app.extensions import db


class AnalyticsTests(DatabaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password_hash = generate_password_hash("test-password-123")

    def setUp(self):
        self.client = self.app.test_client()
        self.visitor = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            users = [User(email=f"{name}@example.com", password_hash=self.password_hash, role=role)
                     for name, role in (("owner", "interior_designer"), ("other", "interior_designer"),
                                        ("new", "interior_designer"), ("guest", "guest"))]
            db.session.add_all(users)
            db.session.flush()
            companies = [Company(owner_id=users[0].id, name="Our Studio"),
                         Company(owner_id=users[1].id, name="Other Studio")]
            db.session.add_all(companies)
            db.session.flush()
            projects = [Project(company_id=companies[0].id, status="current", title="Our Current", description="<script>Text</script>"),
                        Project(company_id=companies[0].id, status="past", title="Our Past"),
                        Project(company_id=companies[1].id, status="past", title="Other Private Metrics")]
            db.session.add_all(projects)
            db.session.flush()
            self.current_id, self.past_id, self.other_id = [p.id for p in projects]
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def token(self, client, path):
        response = client.get(path)
        self.assertEqual(response.status_code, 200)
        return re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.get_data(as_text=True)).group(1)

    def login(self, name="owner"):
        response = self.client.post("/login", data={"csrf_token": self.token(self.client, "/login"),
            "email": f"{name}@example.com", "password": "test-password-123"})
        self.assertEqual(response.status_code, 302)

    def public_path(self, project_id=None):
        return f"/portfolio/projects/{project_id or self.current_id}"

    def count(self, entity, project_id=None):
        with self.app.app_context():
            return db.session.scalar(db.select(db.func.count()).select_from(entity).where(
                entity.project_id == (project_id or self.current_id)))

    def shortlist(self, client=None, project_id=None, **extra):
        client = client or self.visitor
        path = self.public_path(project_id)
        return client.post(path + "/shortlist", data={"csrf_token": self.token(client, path), **extra})

    def test_counts_include_both_statuses_zeroes_and_do_not_multiply(self):
        with self.app.app_context():
            db.session.add_all([ProjectView(project_id=self.current_id) for _ in range(2)])
            db.session.add_all([Shortlist(project_id=self.current_id, visitor_token=str(i)) for i in range(3)])
            db.session.add(ProjectView(project_id=self.other_id))
            db.session.commit()
        self.login()
        for metric, expected in (("views", 2), ("shortlists", 3)):
            listing = self.client.get(f"/analytics/{metric}")
            self.assertEqual(listing.status_code, 200)
            self.assertIn(b"Our Current", listing.data)
            self.assertIn(b"Our Past", listing.data)
            self.assertNotIn(b"Other Private Metrics", listing.data)
            for project_id, count in ((self.current_id, expected), (self.past_id, 0)):
                response = self.client.get(f"/projects/{project_id}/analytics/{metric}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(re.findall(rb"<td>(\d+)</td>", response.data), [str(count).encode()])

    def test_analytics_require_authentication_role_and_ownership(self):
        paths = ("/analytics/views", "/analytics/shortlists",
                 f"/projects/{self.current_id}/analytics/views", f"/projects/{self.current_id}/analytics/shortlists")
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 302)
        self.login("guest")
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 403)
        self.client.post("/logout", data={"csrf_token": self.token(self.client, "/dashboard")})
        self.login()
        for metric in ("views", "shortlists"):
            for project_id in (self.other_id, 99999):
                self.assertEqual(self.client.get(f"/projects/{project_id}/analytics/{metric}").status_code, 404)
            self.assertEqual(self.client.post(f"/analytics/{metric}", data={
                "csrf_token": self.token(self.client, "/dashboard")}).status_code, 405)

    def test_no_company_empty_state_and_navigation(self):
        self.login("new")
        for metric in ("views", "shortlists"):
            self.assertIn(b"No projects yet", self.client.get(f"/analytics/{metric}").data)
            self.assertIn(f'href="/analytics/{metric}"'.encode(), self.client.get("/dashboard").data)

    def test_public_page_records_deduplicated_visits_with_expiry(self):
        with patch("app.public_projects.time", return_value=1000):
            response = self.visitor.get(self.public_path())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertIn(b"Our Studio", response.data)
            self.assertIn(b"&lt;script&gt;Text&lt;/script&gt;", response.data)
            self.assertNotIn(b"analytics/", response.data)
        with patch("app.public_projects.time", return_value=1001):
            self.visitor.get(self.public_path())
            self.visitor.get(self.public_path(self.past_id))
        self.assertEqual(self.count(ProjectView), 1)
        self.assertEqual(self.count(ProjectView, self.past_id), 1)
        with patch("app.public_projects.time", return_value=2800):
            self.visitor.get(self.public_path())
        self.assertEqual(self.count(ProjectView), 2)
        self.app.test_client().get(self.public_path())
        self.assertEqual(self.count(ProjectView), 3)

    def test_head_missing_projects_and_private_pages_do_not_count(self):
        self.assertEqual(self.visitor.head(self.public_path()).status_code, 200)
        self.assertEqual(self.visitor.get(self.public_path(99999)).status_code, 404)
        self.assertEqual(self.count(ProjectView), 0)
        self.login()
        for project_id, status in ((self.current_id, "current"), (self.past_id, "past")):
            for path in (f"/projects/{status}/{project_id}", f"/projects/{project_id}/analytics/views",
                         f"/projects/{project_id}/analytics/shortlists", self.public_path(project_id)):
                self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.count(ProjectView), 0)
        self.assertEqual(self.count(ProjectView, self.past_id), 0)

    def test_owner_cannot_shortlist_own_project(self):
        self.login()
        response = self.client.get(self.public_path())
        self.assertIn(b"previewing your own", response.data)
        self.assertNotIn(b">Shortlist project</button>", response.data)
        for project_id in (self.current_id, self.past_id):
            response = self.client.post(self.public_path(project_id) + "/shortlist", data={
                "csrf_token": self.token(self.client, "/dashboard")})
            self.assertEqual(response.status_code, 403)
            self.assertEqual(self.count(Shortlist, project_id), 0)

    def test_shortlists_deduplicate_per_project_and_browser(self):
        response = self.shortlist(visitor_token="forged", project_id=self.current_id)
        self.assertEqual(response.status_code, 302)
        public = self.visitor.get(response.location)
        self.assertIn(b"You have shortlisted", public.data)
        with self.visitor.session_transaction() as state:
            token = state["visitor_token"]
        self.assertEqual(len(token), 64)
        self.assertNotEqual(token, "forged")
        # Submit the same valid browser form repeatedly, including the redirect.
        for _ in range(3):
            self.assertEqual(self.visitor.post(self.public_path() + "/shortlist", data={
                "csrf_token": self.token(self.visitor, "/login")}, follow_redirects=True).status_code, 200)
        self.assertEqual(self.count(Shortlist), 1)
        self.assertEqual(self.count(ProjectView), 1)
        self.assertEqual(self.shortlist(project_id=self.past_id).status_code, 302)
        self.assertEqual(self.count(Shortlist, self.past_id), 1)
        self.shortlist(client=self.app.test_client())
        self.assertEqual(self.count(Shortlist), 2)
        with self.app.app_context():
            stored = db.session.scalar(db.select(Shortlist).filter_by(project_id=self.current_id, visitor_token=token))
            self.assertIsNotNone(stored)

    def test_shortlist_duplicate_race_rolls_back_and_returns_success(self):
        self.shortlist()
        with self.app.app_context():
            existing = db.session.scalar(db.select(Shortlist))
        # Simulate an insert racing with another request after its initial lookup.
        token = self.token(self.visitor, "/login")
        with patch("app.public_projects.find_shortlist", side_effect=[None, existing]):
            response = self.visitor.post(self.public_path() + "/shortlist", data={"csrf_token": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.count(Shortlist), 1)
        self.assertEqual(self.visitor.get(response.location).status_code, 200)

    def test_shortlist_requires_post_csrf_and_existing_project(self):
        path = self.public_path() + "/shortlist"
        for data in ({}, {"csrf_token": "invalid"}):
            self.assertEqual(self.visitor.post(path, data=data).status_code, 400)
        self.assertEqual(self.visitor.get(path).status_code, 405)
        token = self.token(self.visitor, self.public_path())
        self.assertEqual(self.visitor.post(self.public_path(99999) + "/shortlist", data={"csrf_token": token}).status_code, 404)
        self.assertEqual(self.count(Shortlist), 0)

    def test_public_records_flow_to_owner_analytics_and_delete_with_project(self):
        self.shortlist()
        self.login()
        for metric in ("views", "shortlists"):
            response = self.client.get(f"/projects/{self.current_id}/analytics/{metric}")
            self.assertIn(b"<td>1</td>", response.data)
        private = self.client.get(f"/projects/current/{self.current_id}")
        self.assertIn(self.public_path().encode(), private.data)
        response = self.client.post(f"/projects/current/{self.current_id}/delete", data={
            "csrf_token": self.token(self.client, "/dashboard"), "confirmation": "delete"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.count(ProjectView), 0)
        self.assertEqual(self.count(Shortlist), 0)
        self.assertEqual(self.visitor.get(self.public_path()).status_code, 404)
        self.assertEqual(self.client.get(f"/projects/{self.current_id}/analytics/views").status_code, 404)

    def test_view_history_is_bounded_and_visitor_token_stays_stable(self):
        with self.visitor.session_transaction() as state:
            state["recent_project_views"] = {str(1000 + i): 1000 + i for i in range(100)}
            state["visitor_token"] = "a" * 64
        with patch("app.public_projects.time", return_value=1200):
            self.visitor.get(self.public_path())
        with self.visitor.session_transaction() as state:
            self.assertEqual(len(state["recent_project_views"]), 100)
            self.assertIn(str(self.current_id), state["recent_project_views"])
            self.assertNotIn("1000", state["recent_project_views"])
            self.assertEqual(state["visitor_token"], "a" * 64)


if __name__ == "__main__":
    unittest.main()
