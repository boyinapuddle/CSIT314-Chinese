# Coursework demonstration

Run from the repository root in Windows PowerShell. Use your existing `.venv` and configured `.env`; do not copy the example over an existing configuration.

## Start and provision sample data

```powershell
.venv\Scripts\Activate.ps1
python -m flask --app run.py init-db
python -m flask --app run.py seed-demo
python -m flask --app run.py run --debug
```

`seed-demo` prompts for a password and confirmation (at least 12 characters). The account defaults to `demo.designer@example.com`; use `--email another-demo@example.com` for a new demonstration. No password is included in the repository. The command refuses any existing account and commits all sample records together. It does not clear tables, reset passwords or overwrite portfolios.

The sample portfolio contains:

| Project | Status | Seeded views | Seeded shortlists |
| --- | --- | --- | --- |
| Serangoon Courtyard Home | Current | 5 | 2 |
| River Valley Compact Studio | Current | 2 | 1 |
| Tiong Bahru Reading House | Past | 8 | 3 |
| East Coast Family Apartment | Past | 0 | 0 |

These counts are synthetic sample data, explicitly marked by the command and project descriptions. New visitor activity adds to them. To demonstrate company creation from empty state, provision a separate account with `python -m flask --app run.py create-designer`.

## Walkthrough of the 19 stories

1. Open http://127.0.0.1:5000/, log in with your provisioned account, and show the protected dashboard (UC06).
2. With a fresh empty designer, open **My company**, create a company, view it, edit it and search one of its saved fields (UC01/02/03/05). Submit a blank or whitespace-only name to show validation.
3. Open **Manage current projects**. Create a title/description, open its details, update it and find it with search (UC08/09/10/12). Past projects must not appear in these results.
4. Repeat under **Manage past projects** for completed work (UC13/14/15/17). Current projects must not appear in past results.
5. Open **View counts** and **Shortlist counts**. Show current/past projects, including the zero-count sample (UC18/19).
6. Copy one project's **Public project page** URL into a separate incognito browser session. Load it and shortlist it without an account. Return to the designer analytics: its views and shortlists each increase by one. Refresh and retry within 30 minutes to show deduplication. Opening the public page as its signed-in owner must not increment views.
7. Delete a disposable current project and a disposable past project through their confirmation pages (UC11/16). Explain that this also removes their views and shortlists. GET confirmation alone must preserve the project.
8. Attempt company deletion while projects exist: it must be blocked. On a disposable designer's company, remove all projects, then confirm company deletion (UC04).
9. Log out and open a private URL to show redirection to login (UC07). Use another provisioned designer to show that another owner's private project/analytics IDs return 404.

Use disposable sample records for the deletion steps. There is no reset command; existing records are intentionally protected from automatic replacement.

## Verification commands

```powershell
# Fast isolated SQLite tests; the PostgreSQL locking test is skipped.
python -m unittest discover -s tests -v

# Full suite using PostgreSQL from .env, with separate temporary schemas.
python scripts/verify_postgres.py
```

The PostgreSQL runner reports connection/schema readiness, creates a randomly named `bce_test_*` schema per test class, and removes only those generated schemas when each class completes. Your normal `public` tables are never cleared. The role needs permission to create schemas in the selected database. Set `TEST_DATABASE_URL` to a separate test database if preferred; never paste credentials into screenshots or committed files.

Normal test cleanup is automatic. If the process is forcibly killed, it may leave a `bce_test_*` schema behind; inspect any such leftover before removing it. There is deliberately no broad cleanup command against your database.

Automated checks exercise HTTP requests, sessions, CSRF, ORM persistence, foreign-key cascades and PostgreSQL parent locking. They do not replace a manual desktop/mobile browser review. The source diagrams and complete story mapping are in [BCE_TRACEABILITY.md](BCE_TRACEABILITY.md).

## Connection troubleshooting

PostgreSQL 18 on this workstation was confirmed on port **5433**. Match the port in `.env` to the server settings; do not assume 5432. A running service does not guarantee the configured port is correct. `init-db` creates missing tables but does not migrate or reset existing ones. If a password contains URL-reserved characters, percent-encode it in `DATABASE_URL`.

Run `verify_postgres.py` first to distinguish an unreachable server from a healthy connection with missing app tables. A failed check suppresses connection strings and passwords in its output.
