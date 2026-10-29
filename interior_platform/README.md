# Havenlyst — Interior Design Project Platform

A Flask + HTML/CSS/JavaScript + SQLite implementation of the supplied 48 user stories. The visual direction is inspired by contemporary interior-design discovery sites, while the feature scope stays limited to the provided stories.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python run.py
```

Open `http://127.0.0.1:5000`.

## Seeded demo logins

| Role | Username | Password |
|---|---|---|
| User Admin | `admin` | `Admin123!` |
| Interior Designer | `designer` | `Designer123!` |
| Customer | `customer` | `Customer123!` |
| Platform Manager | `manager` | `Manager123!` |

## Current scope

All six parts of the supplied user-story list are represented. See `docs/architecture.md` for endpoint mapping and the 91-class inventory.


## User-story controller traceability

All **48 user stories have their own dedicated Control/Controller class** in `app/controllers.py`. The project currently contains **91 classes total**. Shared services/repositories are still used beneath the controllers so business logic and SQL are not duplicated. See `docs/architecture.md` for the complete story-to-controller table.

## Testing readiness

A pytest setup and starter tests are included now so later TDD evidence can build on a stable harness. Run:

```bash
pytest -q
pytest --cov=app --cov-report=term-missing
```

The repository also includes `.github/workflows/ci.yml`. It runs the tests automatically on push and pull requests. For your eventual coursework evidence, take screenshots from GitHub Actions showing a failing test first, the implementation commit, and then the passing run for the same feature.

## Future test-data plan

The schema is suitable for a generator that can create thousands of accounts/projects/views/favourites. When you move to the testing deliverable, add deterministic bulk fixtures (fixed random seed), boundary/invalid rows, duplicate favourites, suspended accounts/profiles, cross-designer ownership attempts, and high-volume view/shortlist records.

## Notes

- SQLite database is created under `instance/platform.sqlite` unless `DATABASE` is set.
- Replace `SECRET_KEY` in production.
- External image URLs in `seed.py` are demo-only and can be replaced with local/static assets later.
