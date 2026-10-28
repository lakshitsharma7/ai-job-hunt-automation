# Evening Sync Script (07:00 PM)
# Scans recruiter replies, schedules interview calendar blocks (.ics), and updates tracker.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = Split-Path -Parent $ScriptDir
Set-Location $BaseDir
python automation\orchestrator.py --cadence evening

