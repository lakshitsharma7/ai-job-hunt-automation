# Sunday Weekly Review Script
# Analyzes application funnel metrics, response rates, and generates optimization recommendations.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = Split-Path -Parent $ScriptDir
Set-Location $BaseDir
python automation\orchestrator.py --cadence weekly

