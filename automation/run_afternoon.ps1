# Afternoon Application Packaging Script (02:00 PM)
# Prepares approval-ready application packages, tailored resumes, and cover letters.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = Split-Path -Parent $ScriptDir
Set-Location $BaseDir
python automation\orchestrator.py --cadence afternoon

