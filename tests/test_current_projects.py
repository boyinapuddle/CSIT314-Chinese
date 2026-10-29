"""Current-project stories with real sessions, CSRF and enforced foreign keys."""
import re
import unittest

from werkzeug.security import generate_password_hash

from database_support import DatabaseTestCase
from app.entities import Company, Project, ProjectView, Shortlist, User
from app.extensions import db


class CurrentProjectTests(DatabaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password_hash = generate_password_hash("test-password-123")

    def setUp(self):
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            users = [User(email=f"{name}@example.com", password_hash=self.password_hash, role=role)
                     for name, role in (("owner", "interior_designer"), ("other", "interior_designer"),
                                        ("new", "interior_designer"), ("guest", "guest"))]
            db.session.add_all(users)
            db.session.flush()
            company = Company(owner_id=users[0].id, name="Our Studio")
            other = Company(owner_id=users[1].id, name="Other Studio")
            db.session.add_all([company, other])
            db.session.flush()
            projects = [Project(company_id=company.id, status="current", title="Warm apartment", description="Oak interiors 100%"),
                        Project(company_id=company.id, status="past", title="Past secret", description="Oak interiors"),
                        Project(company_id=other.id, status="current", title="Other secret", description="Oak interiors")]
            db.session.add_all(projects)
            db.session.flush()
            self.company_id, self.other_company_id = company.id, other.id
            self.project_id, self.past_id, self.other_id = [p.id for p in projects]
            for project in projects:
                db.session.add_all([ProjectView(project_id=project.id),
                                    Shortlist(project_id=project.id, visitor_token="visitor")])
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def token(self, path="/dashboard"):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        return re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.get_data(as_text=True)).group(1)

    def login(self, name="owner"):
        response = self.client.post("/login", data={"csrf_token": self.token("/login"),
            "email": f"{name}@example.com", "password": "test-password-123"})
        self.assertEqual(response.status_code, 302)

    def post(self, path, **data):
        return self.client.post(path, data={"csrf_token": self.token(), **data})

    def test_create_persists_text_and_ignores_company_and_status_input(self):
        self.login()
        response = self.post("/projects/current/create", title="  New home  ", description="  Calm spaces  ",
                             company_id=self.other_company_id, status="past")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"Calm spaces", self.client.get(response.location).data)
        with self.app.app_context():
            project = db.session.scalar(db.select(Project).where(Project.title == "New home"))
            self.assertEqual((project.company_id, project.status, project.description),
                             (self.company_id, "current", "Calm spaces"))
            self.assertIsNotNone(project.created_at)
        self.assertEqual(self.post("/projects/current/create", title="Title only").status_code, 302)

    def test_create_and_update_validation_preserve_saved_data(self):
        self.login()
        edit = f"/projects/current/{self.project_id}/edit"
        self.assertIn(b'value="Warm apartment"', self.client.get(edit).data)
        for path in ("/projects/current/create", edit):
            for data in ({}, {"title": "   "}, {"title": "x" * 201},
                         {"title": "Valid", "description": "x" * 10001}):
                with self.subTest(path=path, fields=list(data)):
                    self.assertEqual(self.post(path, **data).status_code, 422)
        with self.app.app_context():
            self.assertEqual(db.session.get(Project, self.project_id).title, "Warm apartment")
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Project)), 3)

    def test_view_list_detail_navigation_and_no_view_tracking(self):
        self.login()
        listing = self.client.get("/projects/current")
        self.assertIn(b"Warm apartment", listing.data)
        for hidden in (b"Past secret", b"Other secret"):
            self.assertNotIn(hidden, listing.data)
        for _ in range(2):
            detail = self.client.get(f"/projects/current/{self.project_id}")
            self.assertIn(b"Oak interiors", detail.data)
            self.assertIn(b"Our Studio", detail.data)
        self.assertIn(b'href="/projects/current"', self.client.get("/dashboard").data)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(ProjectView)), 3)

    def test_update_preserves_owner_status_and_created_date(self):
        self.login()
        with self.app.app_context():
            created_at = db.session.get(Project, self.project_id).created_at
        path = f"/projects/current/{self.project_id}/edit"
        response = self.post(path, title="Changed", description="<script>alert(1)</script>",
                             company_id=self.other_company_id, status="past")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"&lt;script&gt;", self.client.get(response.location).data)
        with self.app.app_context():
            project = db.session.get(Project, self.project_id)
            self.assertEqual((project.company_id, project.status, project.created_at),
                             (self.company_id, "current", created_at))
            self.assertEqual(project.title, "Changed")
        self.assertEqual(self.post(path, title="Changed", description="").status_code, 302)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Project, self.project_id).description)

    def test_search_is_literal_and_scoped_to_current_owned_projects(self):
        self.login()
        for query in ("WARM", "oak", "100%"):
            response = self.client.get("/projects/current/search", query_string={"q": query})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Warm apartment", response.data)
            self.assertNotIn(b"Past secret", response.data)
            self.assertNotIn(b"Other secret", response.data)
        for query in ("secret", "_", "' OR 1=1 --", "%not-real%"):
            self.assertIn(b"No matching current projects", self.client.get(
                "/projects/current/search", query_string={"q": query}).data)
        self.assertIn(b"Enter a word", self.client.get("/projects/current/search?q=%20").data)
        self.assertEqual(self.client.get("/projects/current/search", query_string={"q": "x" * 201}).status_code, 422)

    def test_delete_confirms_and_cascades_only_target_project_analytics(self):
        self.login()
        path = f"/projects/current/{self.project_id}/delete"
        confirmation = self.client.get(path)
        self.assertEqual(confirmation.status_code, 200)
        self.assertIn(b"1 view(s) and 1 shortlist(s)", confirmation.data)
        self.assertEqual(self.post(path).status_code, 422)
        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Project, self.project_id))
        self.assertEqual(self.post(path, confirmation="delete").status_code, 302)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Project, self.project_id))
            for entity in (Project, ProjectView, Shortlist):
                self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(entity)), 2)
            self.assertIsNotNone(db.session.get(Company, self.company_id))
        # Past projects still prevent company deletion.
        self.assertEqual(self.post(f"/companies/{self.company_id}/delete", confirmation="delete").status_code, 409)

    def test_other_owners_past_projects_and_missing_ids_are_rejected(self):
        self.login()
        for project_id in (self.past_id, self.other_id, 99999):
            for suffix in ("", "/edit", "/delete"):
                self.assertEqual(self.client.get(f"/projects/current/{project_id}{suffix}").status_code, 404)
            for suffix in ("/edit", "/delete"):
                self.assertEqual(self.post(f"/projects/current/{project_id}{suffix}", title="Hacked",
                                           confirmation="delete").status_code, 404)
        with self.app.app_context():
            self.assertEqual(db.session.get(Project, self.past_id).title, "Past secret")
            self.assertEqual(db.session.get(Project, self.other_id).title, "Other secret")

    def test_requires_company_and_shows_empty_states(self):
        self.login("new")
        for path in ("/projects/current", "/projects/current/search?q=Oak"):
            self.assertIn(b"Create your company", self.client.get(path).data)
        for response in (self.client.get("/projects/current/create"),
                         self.post("/projects/current/create", title="No company")):
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith("/company/create"))
        self.post("/company/create", name="New Studio")
        self.assertIn(b"haven't added any", self.client.get("/projects/current").data)
        self.assertIn(b"No matching", self.client.get("/projects/current/search?q=Oak").data)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Project)), 3)

    def test_authentication_role_csrf_and_read_only_methods(self):
        paths = ("/projects/current", "/projects/current/search", "/projects/current/create",
                 f"/projects/current/{self.project_id}", f"/projects/current/{self.project_id}/edit",
                 f"/projects/current/{self.project_id}/delete")
        mutations = (paths[2], paths[4], paths[5])
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 302)
        token = self.token("/login")
        for path in mutations:
            self.assertEqual(self.client.post(path, data={"csrf_token": token}).status_code, 302)
        self.login("guest")
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 403)
        for path in mutations:
            self.assertEqual(self.post(path, title="Denied", confirmation="delete").status_code, 403)
        self.post("/logout")
        self.login()
        for path in mutations:
            for data in ({}, {"csrf_token": "invalid"}):
                self.assertEqual(self.client.post(path, data=data).status_code, 400)
        for path in (paths[0], paths[1], paths[3]):
            self.assertEqual(self.post(path).status_code, 405)


if __name__ == "__main__":
    unittest.main()
