"""Company stories through HTTP, real sessions, CSRF and an isolated database."""
import re
import unittest

from database_support import DatabaseTestCase
from app.entities import Company, Project, ProjectView, Shortlist, User
from app.extensions import db


class CompanyTests(DatabaseTestCase):

    def setUp(self):
        with self.app.app_context():
            db.create_all()
            for email, role in (("owner@example.com", "interior_designer"),
                                ("other@example.com", "interior_designer"),
                                ("guest@example.com", "guest")):
                user = User(email=email, role=role)
                user.set_password("test-password-123")
                db.session.add(user)
            db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def token(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.get_data(as_text=True))
        self.assertIsNotNone(match)
        return match.group(1)

    def login(self, email="owner@example.com"):
        return self.client.post("/login", data={
            "email": email, "password": "test-password-123",
            "csrf_token": self.token("/login"),
        })

    def create(self, **fields):
        data = {"name": "Studio One", "email": "studio@example.com",
                "description": "Warm homes", "phone": "+65 1234 5678", "address": "Singapore"}
        data.update(fields)
        data["csrf_token"] = self.token("/company/create")
        return self.client.post("/company/create", data=data)

    def company_id(self):
        with self.app.app_context():
            return db.session.scalar(db.select(Company.id))

    def test_create_view_and_one_company_rule(self):
        self.login()
        self.assertIn(b"haven't created", self.client.get("/company").data)
        response = self.create(name="  Studio One  ", owner_id="2")
        self.assertEqual(response.status_code, 302)
        detail = self.client.get(response.location)
        for value in (b"Studio One", b"Warm homes", b"studio@example.com", b"Singapore", b"+65 1234 5678"):
            self.assertIn(value, detail.data)
        with self.app.app_context():
            company = db.session.scalar(db.select(Company))
            self.assertEqual(company.owner.email, "owner@example.com")
            self.assertEqual(company.name, "Studio One")
        self.assertEqual(self.client.post("/company/create", data={
            "name": "Duplicate", "csrf_token": self.token(response.location),
        }).status_code, 302)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Company)), 1)

    def test_create_validation_and_optional_fields(self):
        self.login()
        for invalid in ({"name": "   "}, {"name": "x" * 201}, {"email": "bad-email"},
                        {"phone": "x" * 41}, {"address": "x" * 501}, {"description": "x" * 10001}):
            with self.subTest(invalid=next(iter(invalid))):
                self.assertEqual(self.create(**invalid).status_code, 422)
                self.assertIsNone(self.company_id())
        self.assertEqual(self.create(email="", phone="", description="", address="").status_code, 302)

    def test_update_persists_valid_fields_and_rejects_invalid_fields(self):
        self.login()
        self.create()
        company_id = self.company_id()
        path = f"/companies/{company_id}/edit"
        self.assertIn(b'value="Studio One"', self.client.get(path).data)
        token = self.token(path)
        self.assertEqual(self.client.post(path, data={"csrf_token": token, "name": " "}).status_code, 422)
        self.assertEqual(self.client.post(path, data={
            "csrf_token": token, "name": "Updated", "email": "new@example.com",
            "description": "New description", "address": "New address", "phone": "123",
            "owner_id": "2",
        }).status_code, 302)
        with self.app.app_context():
            company = db.session.get(Company, company_id)
            self.assertEqual((company.name, company.email, company.address, company.phone, company.description),
                             ("Updated", "new@example.com", "New address", "123", "New description"))
            self.assertEqual(company.owner.email, "owner@example.com")

    def test_search_is_literal_case_insensitive_and_owner_scoped(self):
        self.login()
        self.create(description="Warm <script>homes</script> 100%")
        with self.app.app_context():
            other = db.session.scalar(db.select(User).filter_by(email="other@example.com"))
            db.session.add(Company(owner_id=other.id, name="Secret Other Studio"))
            db.session.commit()
        for query, expected in (("WARM", b"Warm &lt;script&gt;"), ("Singapore", b"Address"),
                                ("studio@", b"Email"), ("1234", b"Phone"), ("Studio One", b"Company name")):
            self.assertIn(expected, self.client.get("/company/search", query_string={"q": query}).data)
        for query in ("Secret", "' OR 1=1 --", "_"):
            self.assertIn(b"No matching", self.client.get("/company/search", query_string={"q": query}).data)
        self.assertIn(b"100%", self.client.get("/company/search?q=%25").data)
        self.assertEqual(self.client.get("/company/search", query_string={"q": "x" * 201}).status_code, 422)
        self.assertNotIn(b"<script>", self.client.get(f"/companies/{self.company_id()}").data)

    def test_delete_requires_confirmation_and_preserves_other_company(self):
        self.login()
        self.create()
        company_id = self.company_id()
        with self.app.app_context():
            other = db.session.scalar(db.select(User).filter_by(email="other@example.com"))
            other_company = Company(owner_id=other.id, name="Other")
            db.session.add(other_company)
            db.session.commit()
            other_id = other_company.id
        path = f"/companies/{company_id}/delete"
        token = self.token(path)
        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Company, company_id))
        self.assertEqual(self.client.post(path, data={"csrf_token": token}).status_code, 422)
        self.assertEqual(self.client.post(path, data={"csrf_token": token, "confirmation": "delete"}).status_code, 302)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Company, company_id))
            self.assertIsNotNone(db.session.get(Company, other_id))

    def test_delete_blocks_projects_and_preserves_analytics(self):
        self.login()
        self.create()
        company_id = self.company_id()
        with self.app.app_context():
            project = Project(company_id=company_id, title="Home", status="current")
            db.session.add(project)
            db.session.flush()
            db.session.add_all([ProjectView(project_id=project.id), Shortlist(project_id=project.id, visitor_token="visitor")])
            db.session.commit()
        path = f"/companies/{company_id}/delete"
        self.assertIn(b"Deletion is blocked", self.client.get(path).data)
        response = self.client.post(path, data={"csrf_token": self.token("/dashboard"), "confirmation": "delete"})
        self.assertEqual(response.status_code, 409)
        with self.app.app_context():
            for entity in (Company, Project, ProjectView, Shortlist):
                self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(entity)), 1)

    def test_cross_owner_and_missing_objects(self):
        self.login()
        self.create()
        company_id = self.company_id()
        self.client.post("/logout", data={"csrf_token": self.token("/dashboard")})
        self.login("other@example.com")
        token = self.token("/dashboard")
        for target_id in (company_id, 99999):
            for suffix in ("", "/edit", "/delete"):
                self.assertEqual(self.client.get(f"/companies/{target_id}{suffix}").status_code, 404)
            for suffix in ("/edit", "/delete"):
                self.assertEqual(self.client.post(f"/companies/{target_id}{suffix}", data={
                    "csrf_token": token, "name": "Hacked", "confirmation": "delete",
                }).status_code, 404)
        self.assertNotIn(b"Studio One", self.client.get("/company/search?q=Studio").data)

    def test_authentication_role_and_csrf_protection(self):
        paths = ("/company", "/company/create", "/company/search", "/companies/1",
                 "/companies/1/edit", "/companies/1/delete")
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 302)
        token = self.token("/login")
        for path in ("/company/create", "/companies/1/edit", "/companies/1/delete"):
            self.assertEqual(self.client.post(path, data={"csrf_token": token}).status_code, 302)
        self.assertEqual(self.login("guest@example.com").status_code, 302)
        for path in paths:
            self.assertEqual(self.client.get(path).status_code, 403)
        for path in ("/company/create", "/companies/1/edit", "/companies/1/delete"):
            self.assertEqual(self.client.post(path, data={"csrf_token": token}).status_code, 403)
        self.client.post("/logout", data={"csrf_token": self.token("/dashboard")})
        self.login()
        self.create()
        for path in ("/company/create", "/companies/1/edit", "/companies/1/delete", "/logout"):
            self.assertEqual(self.client.post(path, data={"name": "Hacked", "confirmation": "delete"}).status_code, 400)
        self.assertEqual(self.client.get("/logout").status_code, 405)

    def test_login_logout_flow(self):
        self.assertEqual(self.client.get("/dashboard").status_code, 302)
        response = self.client.post("/login", data={"email": "owner@example.com", "password": "wrong",
                                                   "csrf_token": self.token("/login")})
        self.assertIn(b"Invalid email or password", response.data)
        self.assertEqual(self.login().status_code, 302)
        self.assertEqual(self.client.get("/dashboard").status_code, 200)
        self.client.post("/logout", data={"csrf_token": self.token("/dashboard")})
        self.assertEqual(self.client.get("/company").status_code, 302)


if __name__ == "__main__":
    unittest.main()
