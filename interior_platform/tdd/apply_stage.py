from pathlib import Path
import shutil
import sys

VALID_STAGES = {"RED", "GREEN", "REFACTOR"}

if len(sys.argv) != 2 or sys.argv[1].upper() not in VALID_STAGES:
    raise SystemExit("Usage: python tdd/apply_stage.py RED|GREEN|REFACTOR")

stage = sys.argv[1].upper()
root = Path(__file__).resolve().parents[1]
stage_root = root / "tdd" / "stages" / stage

for filename in ("entities.py", "repositories.py", "controllers.py", "boundaries.py", "routes.py"):
    shutil.copy2(stage_root / "app" / filename, root / "app" / filename)


print(f"Applied TDD stage: {stage}")
