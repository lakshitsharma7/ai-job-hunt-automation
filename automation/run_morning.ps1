# Morning Job Hunt Discovery Script (10:00 AM)
# Discovers jobs across permitted portals, applies anti-scam checks, and calculates fit scores.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = Split-Path -Parent $ScriptDir
Set-Location $BaseDir
python automation\orchestrator.py --cadence morning

