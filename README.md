# Interior Designer Portfolio — BCE Starter

Flask + Jinja/HTML/CSS/JS + PostgreSQL. The project intentionally has no image functionality.

## Scope
19 user stories, **18 controllers** (login/logout share `auth_controller.py`).

**Implemented in Phase 1:** secure login/logout, protected dashboard, user entity, shared database entities, styling, CSRF protection, a CLI command for provisioning designer accounts, and a CLI command to create the schema for local development.

**Implemented in Phase 2:** all five company stories, with separate controllers, shared company boundaries, server-side validation, ownership and designer-role checks, CSRF-protected forms, and automated HTTP tests.

**Implemented in Phase 3:** all five current-project stories, with separate controllers, reusable project forms and queries, owner/status checks, confirmation before deletion, navigation and automated HTTP tests.

**Implemented in Phase 4:** all five past-project stories, with independent controllers, shared project boundaries, owner/status checks, validation, confirmed deletion and automated HTTP tests.

**Implemented in Phase 5:** both owner-only analytics stories and minimal public project pages for recording visits and anonymous shortlists. All 19 stories now have implemented controllers; the 18-controller structure is preserved.

**Implemented in Phase 6:** non-destructive demo provisioning, a complete 19-story BCE mapping with implementation diagrams, PostgreSQL test isolation, an architecture check, database locking verification, refined responsive styling, keyboard skip navigation and shared error pages. See [the demo guide](docs/DEMO_GUIDE.md) and [BCE traceability](docs/BCE_TRACEABILITY.md).

## Local setup

1. Install Python 3.11+ and PostgreSQL 15+.
2. In PostgreSQL, using an admin account, execute:

   ```sql
   CREATE ROLE id_user LOGIN PASSWORD 'change_this_password';
   CREATE DATABASE id_platform OWNER id_user;
   ```

3. From the project folder:

   ```bash
   python -m venv .venv
   # macOS/Linux: source .venv/bin/activate
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
   ```

4. Change the example database password in PostgreSQL and `.env` before use. Set a strong random `SECRET_KEY` (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`). Never commit `.env`. Match the URL port to your server: this workstation's PostgreSQL 18 listens on **5433**, which is reflected in `.env.example`.
5. Set up tables and provision a designer account:

   ```bash
   flask --app run.py init-db
   flask --app run.py create-designer
   flask --app run.py run --debug
   ```

6. Open http://127.0.0.1:5000/ . Use the email/password you created.

`init-db` uses `create_all` for initial local development only. Use schema migrations before changing a deployed database.

## BCE mapping

The complete mapping of all 19 stories to controller handlers, routes, boundaries, entities, tests and sequence diagrams is in [docs/BCE_TRACEABILITY.md](docs/BCE_TRACEABILITY.md). These diagrams were derived from the implementation; no assignment UML was supplied for comparison.

- **Boundary**: `app/templates/`, `app/static/` (browser UI).
- **Controller**: `app/controllers/` (one Python module per user story, with one deliberate auth exception).
- **Entity**: `app/entities/` (SQLAlchemy ORM classes shared between controllers).

## Company management

After logging in, choose **Manage company** on the dashboard or **My company** in the navigation. Create a company, view its saved fields, edit them, search details, or open its deletion confirmation page.

The flow is **Boundary (Jinja form/page) -> story Controller -> Company Entity -> PostgreSQL**. `app/company_support.py` shares forms and ownership helpers; each story still has its own controller and routes.

| Story | Controller in `app/controllers/` | Route | Boundary in `app/templates/company/` | Tests in `tests/test_company.py` |
| --- | --- | --- | --- | --- |
| UC01 Create | `create_company_controller.py` | GET/POST `/company/create` | `form.html` | `test_create_view_and_one_company_rule`, `test_create_validation_and_optional_fields` |
| UC02 View | `view_company_controller.py` | GET `/company`, `/companies/<id>` | `detail.html` | `test_create_view_and_one_company_rule` |
| UC03 Update | `update_company_controller.py` | GET/POST `/companies/<id>/edit` | `form.html` | `test_update_persists_valid_fields_and_rejects_invalid_fields` |
| UC04 Delete | `delete_company_controller.py` | GET/POST `/companies/<id>/delete` | `delete.html` | `test_delete_requires_confirmation_and_preserves_other_company`, `test_delete_blocks_projects_and_preserves_analytics` |
| UC05 Search | `search_company_controller.py` | GET `/company/search?q=...` | `search.html` | `test_search_is_literal_case_insensitive_and_owner_scoped` |

All five use `Company` and the authenticated `User`; deletion also checks `Project`. Shared authorization tests cover unauthenticated requests, other owners, nonexistent IDs, non-designer roles, and missing CSRF tokens. Authentication has a login/logout regression test.

Assumptions and behavior:

- One company per designer, enforced by the existing unique owner constraint. Submitted owner IDs are ignored; the session identifies the owner. Other owners' company IDs return 404.
- Only company name is required (maximum 200 characters). Optional email, phone, and address are limited to 254, 40, and 500 characters. Description is limited to 10,000 characters. Email has basic format validation; all fields are trimmed. Invalid forms retain input and return 422.
- Search finds literal, case-insensitive substrings in the owner's name, description, email, phone and address. It returns matching fields, not other companies. Search terms are limited to 200 characters.
- GET deletion only displays confirmation. POST requires CSRF and an explicit confirmation checkbox. Companies with projects cannot be deleted (409); projects and their analytics are preserved. The PostgreSQL parent row is locked during the dependency check to prevent concurrent project insertion. No tables or foreign keys have changed, so this phase needs no schema migration.
- Current and past projects can be removed through their confirmation pages. Company deletion remains blocked until all its projects have been removed. Do not reset the database to work around this safeguard.

## Current project management (Phase 3)

Choose **Manage current projects** on the dashboard or **Current projects** in the navigation. Create your company first, then add a project with a required title (maximum 200 characters) and optional description (maximum 10,000 characters). Fields are trimmed and invalid submissions return 422 with field errors. Project pages render text safely through Jinja escaping.

The flow is **Boundary -> story Controller -> Project / Company Entity -> PostgreSQL**. Forms and ownership queries live in `app/project_support.py`; each of the five controllers retains its own request handling. No database schema changes or new dependencies are required.

| Story | Controller in `app/controllers/` | Route | Boundary in `app/templates/projects/current/` | Tests in `tests/test_current_projects.py` |
| --- | --- | --- | --- | --- |
| UC08 Create | `create_current_project_controller.py` | GET/POST `/projects/current/create` | `form.html` | `test_create_persists_text_and_ignores_company_and_status_input` |
| UC09 View | `view_current_project_controller.py` | GET `/projects/current`, `/projects/current/<id>` | `list.html`, `detail.html` | `test_view_list_detail_navigation_and_no_view_tracking` |
| UC10 Update | `update_current_project_controller.py` | GET/POST `/projects/current/<id>/edit` | `form.html` | `test_update_preserves_owner_status_and_created_date`, `test_create_and_update_validation_preserve_saved_data` |
| UC11 Delete | `delete_current_project_controller.py` | GET/POST `/projects/current/<id>/delete` | `delete.html` | `test_delete_confirms_and_cascades_only_target_project_analytics` |
| UC12 Search | `search_current_project_controller.py` | GET `/projects/current/search?q=...` | `list.html` | `test_search_is_literal_and_scoped_to_current_owned_projects` |

- Every query checks the authenticated owner and `status='current'`. Past projects, other owners' projects and nonexistent IDs return 404 on detail/edit/delete routes. Lists and search exclude them. Role and CSRF checks apply to all mutations.
- Creation derives `company_id` from the session and fixes status to `current`. Editing changes only title and description, preserving the company, status and creation date. Submitted company/status fields are ignored.
- Search matches a literal case-insensitive substring in the title or description, with a maximum of 200 characters. SQL wildcard characters such as `%` and `_` are escaped. Blank searches prompt for input. Lists and search results show newest projects first.
- Deletion requires POST, CSRF and an explicit confirmation checkbox. The confirmation page warns that all recorded views and shortlists will also be deleted and shows their current counts. The existing database foreign keys cascade deletion only for that project; the company and other projects remain.
- Designer list/detail requests do not record public views. Public engagement is recorded only through the public project pages described in Phase 5.
- Tests also cover missing companies, empty lists, forged IDs/status, cross-owner access, past-project exclusion, authentication, roles, CSRF, validation and preservation of unrelated records.

## Past project management (Phase 4)

Choose **Manage past projects** on the dashboard or **Past projects** in the navigation to manage completed work. A company is required before creating a project. Title is required (maximum 200 characters); description is optional (maximum 10,000 characters). Both fields are trimmed, validation errors retain input and return 422, and Jinja escapes submitted text.

| Story | Controller in `app/controllers/` | Route | Boundary in `app/templates/projects/past/` | Tests in `tests/test_past_projects.py` |
| --- | --- | --- | --- | --- |
| UC13 Create | `create_past_project_controller.py` | GET/POST `/projects/past/create` | `form.html` | `test_create_persists_text_and_ignores_company_and_status_input` |
| UC14 View | `view_past_project_controller.py` | GET `/projects/past`, `/projects/past/<id>` | `list.html`, `detail.html` | `test_view_list_detail_navigation_and_no_view_tracking` |
| UC15 Update | `update_past_project_controller.py` | GET/POST `/projects/past/<id>/edit` | `form.html` | `test_update_preserves_owner_status_and_created_date`, `test_create_and_update_validation_preserve_saved_data` |
| UC16 Delete | `delete_past_project_controller.py` | GET/POST `/projects/past/<id>/delete` | `delete.html` | `test_delete_confirms_and_cascades_only_target_project_analytics` |
| UC17 Search | `search_past_project_controller.py` | GET `/projects/past/search?q=...` | `list.html` | `test_search_is_literal_and_scoped_to_past_owned_projects` |

The BCE flow is **Boundary -> story Controller -> shared Project / Company Entity -> PostgreSQL**. The current and past boundary files are small wrappers around shared templates in `app/templates/projects/`. Each wrapper sets its display status and links to the relevant story controllers. Authorization and status filtering remain server-side in the controllers and shared query helpers. No schema changes or new dependencies are required.

- Every past-project query checks ownership and `status='past'`. Current projects, other owners' projects and nonexistent IDs return 404 through past detail/edit/delete routes; they are excluded from lists/search. Current routes enforce the reverse isolation.
- Creation derives the company from the session and fixes status to `past`. Updates change only title and description. Submitted company IDs and status values are ignored; neither workflow changes a project between current and past.
- Search covers titles and descriptions with a literal, case-insensitive substring of at most 200 characters. `%` and `_` are escaped. Blank searches prompt for input. Results are ordered newest first.
- Deletion uses POST with CSRF and explicit confirmation. The confirmation warns about deleting the project's recorded views and shortlists and displays their counts. Existing database cascades remove only that project's analytics. Other projects and the company remain.
- Viewing private past-project pages does not record public views. Phase 5 provides separate public project pages for engagement recording.
- Tests cover authentication, designer roles, CSRF, validation, missing companies, empty states, owner/status isolation, forged input, escaped text, shared boundary labels and links, analytics cascades, and company deletion after both current and past projects are removed.

## Project analytics (Phase 5)

Choose **View counts** or **Shortlist counts** in the dashboard's Engagement tile. Each page lists your current and past projects, including projects with zero engagement. Each private project detail page also links to its individual analytics and public page. Other owners' project IDs and nonexistent IDs return 404 on individual analytics routes. All analytics routes require a signed-in Interior Designer.

| Story | Controller in `app/controllers/` | GET routes | Boundary | Entities | Tests in `tests/test_analytics.py` |
| --- | --- | --- | --- | --- | --- |
| UC18 View number of views | `view_project_views_controller.py` | `/analytics/views`, `/projects/<id>/analytics/views` | `analytics/counts.html` | `Project`, `Company`, `ProjectView` | `test_counts_include_both_statuses_zeroes_and_do_not_multiply`, `test_analytics_require_authentication_role_and_ownership` |
| UC19 View number of shortlists | `view_project_shortlists_controller.py` | `/analytics/shortlists`, `/projects/<id>/analytics/shortlists` | `analytics/counts.html` | `Project`, `Company`, `Shortlist` | Same count/access tests plus `test_shortlists_deduplicate_per_project_and_browser` |

The BCE flow is **Boundary -> story Controller -> Project / Company / metric Entity -> PostgreSQL**. `app/analytics_support.py` shares owner-scoped count queries. Separate count subqueries avoid multiplying views by shortlists. Existing tables, foreign keys and the shortlist unique constraint are reused; no schema changes or additional dependencies are required.

Minimal public engagement support lives in `app/public_projects.py`, outside the 18 story-controller modules. It supports the two count stories rather than adding new formal stories:

- GET `/portfolio/projects/<id>` shows the project's company name, status, title and description, with a shortlist button. Share this URL from the private project detail page. There is no public directory, customer account, image upload or private analytics on this page. Both current and past projects are accessible through their public links.
- Public GET visits create `ProjectView` records. A signed browser session remembers recent project visits and suppresses repeats for 30 minutes per project. A visit at or after that window counts again. HEAD requests, missing projects, private workspace/analytics pages and the owner's signed-in public previews do not count. A different signed-in designer may count as a visitor to another designer's project.
- Counts represent recorded visits, not globally unique people. The browser's recent history is capped at 100 projects to bound cookie size; visiting an evicted project may count again within 30 minutes. Clearing cookies, using another browser or parallel requests can produce additional counts. This is a simple coursework metric, not bot detection or fraud-resistant analytics.
- POST `/portfolio/projects/<id>/shortlist` requires CSRF and uses a server-generated 64-character visitor token held in the signed browser session. Submitted visitor IDs are ignored. The existing unique `(project_id, visitor_token)` constraint prevents repeated or racing submissions from adding duplicate shortlists. Repeated requests return success, and the public page shows the saved state.
- Shortlists count browser tokens, not identified people. Clearing cookies or switching browsers creates a different token. Shortlists persist in the database after the browser session ends. There is no removal action because the supplied stories only require counts. Owners cannot shortlist their own projects while signed in.
- Public pages use `Cache-Control: no-store` so browsers do not reuse another visit's personalized shortlist state. Deleting a project still removes its associated views and shortlists through the existing foreign keys.

Phase 5 tests cover zero/nonzero counts, both project statuses, owner access, authentication, roles, missing IDs, browser deduplication and expiry, independent visitors, HEAD requests, owner previews, CSRF, repeated/racing shortlist submissions, bounded visit history, and deletion of generated analytics.

## Run and test (Windows PowerShell)

After completing the one-time setup above, normal sessions use:

```powershell
.venv\Scripts\Activate.ps1
python -m flask --app run.py run --debug
```

Open http://127.0.0.1:5000/ and log in with the account provisioned through `create-designer`.

Run tests from the project folder with the same environment:

```powershell
python -m unittest discover -s tests -v
```

Tests require only `requirements.txt`. By default they use fresh in-memory SQLite with foreign keys enabled and exercise real login sessions and CSRF. The PostgreSQL-specific locking test is skipped in this mode. To run the same suite against PostgreSQL:

```powershell
python scripts/verify_postgres.py
```

The runner reads `DATABASE_URL` from the environment or `.env` (or an explicit `TEST_DATABASE_URL` override), checks connectivity and application-table readiness, and creates an isolated `bce_test_*` schema for each test class. Normal cleanup removes only those generated schemas; existing `public` tables and records are preserved. The role must have permission to create schemas in the selected database. If `TEST_DATABASE_URL` is already set, direct `unittest` runs also use that isolated PostgreSQL mode. `init-db` creates missing tables only; it does not migrate or clear existing records.

For Phases 3 and 4, also create a current and a past project, restart Flask and verify their saved detail pages, edit and search their text, then delete them through their confirmation pages. Check that each list shows only its own status and that your company remains after project deletion.

For Phase 5, create a project and copy its **Public project page** URL into a separate private/incognito browser session. Visit and shortlist it there, then return to the signed-in designer's analytics pages: the project should have one recorded visit and one shortlist. Refresh the public page and retry the shortlist within 30 minutes; neither count should increase. Your signed-in owner preview should also leave the counts unchanged. Restart Flask and verify that the counts remain in PostgreSQL.

Verification on 29 October 2026: **45 tests pass on PostgreSQL 18.6**. The default SQLite run passes 44 tests and skips the PostgreSQL-only locking check. The suite covers all stories plus safe demo provisioning and the 18-controller routing constraint. The PostgreSQL check confirms that a parent company lock blocks a concurrent referencing project insert; it does not claim broad load testing. Manual desktop/mobile browser review and comparison against any later supplied assignment UML remain separate review steps.

## Sample portfolio and coursework demo

After `init-db`, optionally provision a new demo account:

```powershell
python -m flask --app run.py seed-demo
```

The command prompts for a password and confirmation, then creates `demo.designer@example.com` with one company, two current projects, two past projects, 15 synthetic views and six synthetic shortlists. Use `--email another-demo@example.com` for a fresh account. Existing emails are rejected without changing their passwords or records. No reset or overwrite is performed. Follow [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for the full 19-story walkthrough, seeded count values, public visitor demonstration and connection troubleshooting.

## Security notes
Passwords are hashed, login errors are generic, logout uses POST + CSRF validation, sessions have HttpOnly and SameSite=Lax settings, and the dashboard requires authentication. In production, configure HTTPS and `SESSION_COOKIE_SECURE=True`, disable debug, use environment-managed secrets, and add login rate limiting. Registration is intentionally not part of the supplied scope: use the CLI for demo accounts.
