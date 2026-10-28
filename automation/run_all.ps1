# Full Pipeline Execution Script
# Executes Morning Discovery -> Afternoon Prep -> Evening Sync -> Weekly Review
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = Split-Path -Parent $ScriptDir
Set-Location $BaseDir
python automation\orchestrator.py --cadence all

