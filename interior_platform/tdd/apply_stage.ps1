param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("RED", "GREEN", "REFACTOR")]
    [string]$Stage
)

$Root = Split-Path -Parent $PSScriptRoot
$StageRoot = Join-Path $PSScriptRoot "stages\$Stage"

Copy-Item "$StageRoot\app\entities.py" "$Root\app\entities.py" -Force
Copy-Item "$StageRoot\app\repositories.py" "$Root\app\repositories.py" -Force
Copy-Item "$StageRoot\app\controllers.py" "$Root\app\controllers.py" -Force
Copy-Item "$StageRoot\app\boundaries.py" "$Root\app\boundaries.py" -Force
Copy-Item "$StageRoot\app\routes.py" "$Root\app\routes.py" -Force
Copy-Item "$StageRoot\tests\test_tdd_five_features.py" "$Root\tests\test_tdd_five_features.py" -Force

Write-Host "Applied TDD stage: $Stage"
