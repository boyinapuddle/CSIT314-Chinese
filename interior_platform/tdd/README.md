# TDD Stage Switcher

Run the stage script from the project root on a clean Git branch or a disposable copy of the project.

```powershell
.\.venv\Scripts\python.exe tdd\apply_stage.py RED
.\.venv\Scripts\python.exe tdd\apply_stage.py GREEN
.\.venv\Scripts\python.exe tdd\apply_stage.py REFACTOR
```

After each stage, run pytest and take the required screenshot. See `docs/tdd_evidence/README.md` for the full procedure.

## Pytest collection

`pytest.ini` limits normal test discovery to the top level `tests/` directory. The archived RED, GREEN and REFACTOR snapshots under `tdd/stages/` are evidence only and are not collected during the final regression run.
