# TDD Evidence for Five Existing Features

This folder provides a reproducible Red, Green, Refactor demonstration for five existing feature areas.

## Features covered

1. User profile creation: profile names are treated as duplicates even when case or internal spacing differs.
2. User account creation: an account cannot be created using a suspended profile.
3. Favourite management: the save controller rejects a non Customer session even if it is called outside the route guard.
4. IDP category creation: category names are treated as duplicates regardless of case or surrounding spacing.
5. Non Customer IDP browsing: the Story 50 controller rejects a Customer session so Customer views cannot bypass Customer view counting.

## How to capture RED

Use a clean copy or a Git branch because the stage script overwrites five application files.

```powershell
.\.venv\Scripts\python.exe tdd\apply_stage.py RED
.\.venv\Scripts\python.exe -m pytest tests\test_tdd_five_features.py -v
```

The five tests are expected to fail on the RED stage because only the tests have been added. Take a screenshot showing the failed tests.

Suggested commit message:

```text
test: add failing tests for five validation and access rules
```

## How to capture GREEN

```powershell
.\.venv\Scripts\python.exe tdd\apply_stage.py GREEN
.\.venv\Scripts\python.exe -m pytest tests\test_tdd_five_features.py -v
```

The GREEN stage contains the minimum implementation for the five tests. Take a screenshot showing the five tests passing.

Suggested commit message:

```text
feat: implement five tested validation and access rules
```

## How to capture REFACTOR

```powershell
.\.venv\Scripts\python.exe tdd\apply_stage.py REFACTOR
.\.venv\Scripts\python.exe -m pytest -q
```

The REFACTOR stage removes repeated validation code by using shared helper functions while preserving the tested behavior. Take a screenshot showing the full regression suite passing.

Suggested commit message:

```text
refactor: centralize text and role validation helpers
```

## What changed in each stage

### RED

Only `tests/test_tdd_five_features.py` is introduced. The existing implementation is intentionally unchanged.

### GREEN

Minimum behavior is added:

* profile names collapse repeated whitespace before duplicate checking
* account creation requires an active profile
* favourite controller checks the Customer role
* category creation performs case insensitive duplicate checking
* non Customer browse flow validates the session role

### REFACTOR

The behavior stays the same. Repeated logic is moved into `_clean_spaces`, `_require_role`, and `_require_non_customer` helpers.

## Evidence to include in the report

Capture three screenshots:

1. RED: five failing tests
2. GREEN: five passing feature tests
3. REFACTOR: the complete test suite still passes

Also include the three commits if you are using Git. This provides stronger evidence that the tests were written before the implementation.

## Final regression test collection

The project keeps the RED, GREEN and REFACTOR application-code snapshots under `tdd/stages/`. The only active detailed TDD test file is `tests/test_tdd_five_features.py`. `pytest.ini` limits normal collection to the active `tests` folder, so the final command can be run safely with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
