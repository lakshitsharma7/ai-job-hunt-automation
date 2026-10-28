@echo off
setlocal enabledelayedexpansion
title Autonomous AI Job Hunt System -- Google Antigravity
color 0B

cd /d "%~dp0"
if exist "automation\orchestrator.py" (
    set "WORKSPACE_DIR=%~dp0"
) else if exist "AI-Job-Hunt" (
    set "WORKSPACE_DIR=%~dp0AI-Job-Hunt"
) else (
    set "WORKSPACE_DIR=%~dp0"
)

:MENU
cls
echo ===============================================================================
echo                AUTONOMOUS AI JOB HUNT SYSTEM - GOOGLE ANTIGRAVITY
echo                            Candidate: Lakshit Sharma
echo ===============================================================================
echo.
echo   [1] Run Full Pipeline Cycle (Discovery + Prep + Sync + Review)
echo   [2] Morning Discovery (10:00 AM - Discover, Filter and Fit-Score Jobs)
echo   [3] Afternoon Application Packaging (02:00 PM - Tailor Resumes and Cover Notes)
echo   [4] Evening Inbox and Calendar Sync (07:00 PM - Recruiter Emails and .ics Invites)
echo   [5] Sunday Weekly Analytics Review (Funnel Conversion and Recommendations)
echo.
echo   [6] Run End-to-End System Verification Tests (test_system.py)
echo   [7] Open Job Hunt Tracker in Excel (Job_Hunt_Tracker.xlsx)
echo   [8] Open Latest Application Batch Review (batch_review.md)
echo   [9] View Master Profile and Answer Bank
echo.
echo   [0] Exit
echo.
echo ===============================================================================
set "choice="
set /p choice="Select an option [0-9]: "

if not defined choice goto MENU
set "choice=!choice: =!"

if "!choice!"=="1" goto RUN_ALL
if "!choice!"=="2" goto RUN_MORNING
if "!choice!"=="3" goto RUN_AFTERNOON
if "!choice!"=="4" goto RUN_EVENING
if "!choice!"=="5" goto RUN_WEEKLY
if "!choice!"=="6" goto RUN_TESTS
if "!choice!"=="7" goto OPEN_TRACKER
if "!choice!"=="8" goto OPEN_BATCH
if "!choice!"=="9" goto VIEW_PROFILE
if "!choice!"=="0" goto EXIT

echo Invalid selection. Please choose an option between 0 and 9.
ping 127.0.0.1 -n 2 >nul
goto MENU

:RUN_ALL
cls
echo ===============================================================================
echo                EXECUTING FULL AUTONOMOUS JOB HUNT PIPELINE
echo ===============================================================================
echo.
python "%WORKSPACE_DIR%\automation\orchestrator.py" --cadence all
echo.
echo ===============================================================================
pause
goto MENU

:RUN_MORNING
cls
echo ===============================================================================
echo                RUNNING MORNING DISCOVERY (10:00 AM CADENCE)
echo ===============================================================================
echo.
python "%WORKSPACE_DIR%\automation\orchestrator.py" --cadence morning
echo.
echo ===============================================================================
pause
goto MENU

:RUN_AFTERNOON
cls
echo ===============================================================================
echo          RUNNING AFTERNOON APPLICATION PACKAGING (02:00 PM CADENCE)
echo ===============================================================================
echo.
python "%WORKSPACE_DIR%\automation\orchestrator.py" --cadence afternoon
echo.
echo ===============================================================================
pause
goto MENU

:RUN_EVENING
cls
echo ===============================================================================
echo             RUNNING EVENING INBOX AND CALENDAR SYNC (07:00 PM CADENCE)
echo ===============================================================================
echo.
python "%WORKSPACE_DIR%\automation\orchestrator.py" --cadence evening
echo.
echo ===============================================================================
pause
goto MENU

:RUN_WEEKLY
cls
echo ===============================================================================
echo                    RUNNING SUNDAY WEEKLY ANALYTICS REVIEW
echo ===============================================================================
echo.
python "%WORKSPACE_DIR%\automation\orchestrator.py" --cadence weekly
echo.
echo ===============================================================================
pause
goto MENU

:RUN_TESTS
cls
echo ===============================================================================
echo               RUNNING SYSTEM VERIFICATION TEST SUITE (11 TESTS)
echo ===============================================================================
echo.
python "%WORKSPACE_DIR%\test_system.py"
echo.
echo ===============================================================================
pause
goto MENU

:OPEN_TRACKER
cls
echo Opening Job Hunt Tracker in Excel...
if exist "%WORKSPACE_DIR%\tracker\Job_Hunt_Tracker.xlsx" (
    start "" "%WORKSPACE_DIR%\tracker\Job_Hunt_Tracker.xlsx"
) else (
    echo Job_Hunt_Tracker.xlsx not found! Run discovery first to generate tracker.
)
ping 127.0.0.1 -n 2 >nul
goto MENU

:OPEN_BATCH
cls
echo Locating latest application batch...
python -c "import os, glob; batches = sorted(glob.glob(r'%WORKSPACE_DIR%\applications\batches\batch_*\batch_review.md')); os.system('start \"\" \"' + batches[-1] + '\"') if batches else print('No batch review found yet!')"
ping 127.0.0.1 -n 2 >nul
goto MENU

:VIEW_PROFILE
cls
echo ===============================================================================
echo                          MASTER PROFILE PREVIEW
echo ===============================================================================
echo.
type "%WORKSPACE_DIR%\profiles\master_profile.md" | more
echo.
echo ===============================================================================
pause
goto MENU

:EXIT
cls
echo Exiting Autonomous AI Job Hunt System. Good luck with your applications!
ping 127.0.0.1 -n 2 >nul
exit /b 0
