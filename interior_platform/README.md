# Havenlyst Interior Design Project Platform

Havenlyst is an interior design project platform built with HTML, CSS and JavaScript on the frontend, Flask on the backend and SQLite for persistence.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe run.py
```

Open `http://127.0.0.1:5000`

## Demo accounts

| Role | Username | Password |
| --- | --- | --- |
| User Admin | admin | Admin123! |
| Interior Designer | designer | Designer123! |
| Customer | customer | Customer123! |
| Platform Manager | manager | Manager123! |

## BCE structure

Every user story has its own Controller mapping. The four login stories share one LoginBoundary and use separate role specific login Controllers. The server determines the role from the linked profile after verifying the credentials.

The program flow is

`Route -> Boundary -> Controller -> Entity -> Repository -> SQLite`

The response returns through the same use case layers.

Ownership sensitive Controllers obtain designer and customer identifiers from the trusted session context rather than editable form values.

The full mapping for all 50 stories is in `docs/architecture.md`.

## Diagrams

The `diagrams` folder contains BCE and sequence diagrams for all 50 user stories. `diagrams/ALL_DIAGRAMS.md` provides a combined view and each story has its own folder with Mermaid source files.

## Tests

Run

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The project includes structural traceability tests for all 50 user stories, authentication tests and access control tests. Additional unit tests can be added per Boundary, Controller and Entity for TDD evidence.

## Large test data

`bulk_seed.py` creates a larger deterministic data set for scale testing.

Run

```powershell
.\.venv\Scripts\python.exe bulk_seed.py
```

## CI

`.github/workflows/ci.yml` runs the test suite in GitHub Actions.

## Additional user stories

User Story 49 covers safe deletion of an unused user profile. User Story 50 covers read only browsing of available IDPs by authenticated non customer roles. The complete wording is in `docs/additional_user_stories.md`.

## TDD evidence stages

Five test first hardening scenarios are included under `tdd/` and `docs/tdd_evidence/`.

Use a clean branch or disposable copy and run:

```powershell
.\.venv\Scripts\python.exe tdd\apply_stage.py RED
.\.venv\Scripts\python.exe -m pytest tests\test_tdd_five_features.py -v

.\.venv\Scripts\python.exe tdd\apply_stage.py GREEN
.\.venv\Scripts\python.exe -m pytest tests\test_tdd_five_features.py -v

.\.venv\Scripts\python.exe tdd\apply_stage.py REFACTOR
.\.venv\Scripts\python.exe -m pytest -q
```

See `docs/tdd_evidence/README.md` for the five features and screenshot procedure.
