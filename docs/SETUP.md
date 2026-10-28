# Autonomous AI Job Hunt Automation — Setup & Developer Guide

This document provides complete instructions for setting up, configuring, and operating the **Autonomous AI Job Hunt Automation System**.

---

## 1. Prerequisites

- **Python**: Version `3.10` or higher (`3.12` recommended)
- **Operating System**: Windows 10/11, macOS, or Linux
- **Office / Document Tools**: Microsoft Word / LibreOffice and Excel (for viewing `.docx` and `.xlsx` artifacts)

---

## 2. Installation & Environment Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/lakshitsharma7/ai-job-hunt-automation.git
   cd ai-job-hunt-automation
   ```

2. **Create and Activate a Virtual Environment**:
   - **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Environment Configuration**:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to configure your candidate details and optional Google API keys.*

---

## 3. Configuring Ground Truth (Profile & Answer Bank)

The system enforces strict **zero-fabrication**. Every generated resume, cover letter, and application answer is drawn exclusively from your profile files:

1. **Create your Master Profile**:
   ```bash
   cp profiles/master_profile.example.md profiles/master_profile.md
   ```
   *Fill out your verified experience, technical stack, verified numbers, and education.*

2. **Create your Answer Bank**:
   ```bash
   cp profiles/answer_bank.example.json profiles/answer_bank.json
   ```
   *Add your standard job application form answers (CTC, notice period, relocation, skill years).*

3. **Configure Role & Location Preferences**:
   ```bash
   cp profiles/job_preferences.example.json profiles/job_preferences.json
   ```

---

## 4. Running the Automation Workflow

You can interact with the system using **`run.bat`** (on Windows) or the Python CLI orchestrator:

### Option A: Using Windows One-Click Dashboard
Double-click `run.bat` in the project root to open the interactive terminal menu.

### Option B: Using the Python CLI Orchestrator
- **Run the full cycle**:
  ```bash
  python automation/orchestrator.py --cadence all
  ```
- **Morning Discovery (10:00 AM)**:
  ```bash
  python automation/orchestrator.py --cadence morning
  ```
- **Afternoon Application Preparation (02:00 PM)**:
  ```bash
  python automation/orchestrator.py --cadence afternoon
  ```
- **Evening Inbox & Calendar Sync (07:00 PM)**:
  ```bash
  python automation/orchestrator.py --cadence evening
  ```
- **Sunday Weekly Conversion Review**:
  ```bash
  python automation/orchestrator.py --cadence weekly
  ```

---

## 5. Core Subsystem Workflows

### A. Generating ATS Resumes
Run the resume engine to build single-column, ATS-parseable vector PDFs and DOCX files:
```bash
python resumes/resume_engine.py
```
Outputs:
- `resumes/<Candidate>-Frontend-Developer.pdf` / `.docx`
- `resumes/<Candidate>-Python-Developer.pdf` / `.docx`
- `resumes/<Candidate>-AI-Automation-Developer.pdf` / `.docx`
- `resumes/<Candidate>-Software-Developer.pdf` / `.docx`

### B. Tailoring Resumes for Dream Jobs
```bash
python resumes/tailor.py
```
*Generates a role-tailored 1-page PDF, 120-word cover note, and a recruiter message under 200 characters.*

### C. Supervised Application Approval
When `automation/orchestrator.py --cadence afternoon` runs, review the generated batch document:
```text
applications/batches/<batch_timestamp>/batch_review.md
```
*Inspect every field before confirming submission. Never auto-submit without review.*

### D. Tracking Applications
The system maintains both [`tracker/Job_Hunt_Tracker.xlsx`](file:///d:/React%20Native/job%20hunt/AI-Job-Hunt/tracker/Job_Hunt_Tracker.xlsx) and `Job_Hunt_Tracker.csv` with 12 standardized columns and status color codes.

---

## 6. Running System Verification Tests

Verify that all 11 modules and scoring calculators are operating with 100% pass status:
```bash
python test_system.py
```

---

## 7. Security & Privacy Guardrails

1. **No Stored Passwords**: The system will never request, store, or type account passwords, OTPs, or government identity numbers.
2. **Anti-Scam Filter**: Automatically skips and blacklists listings requiring security deposits, training fees, or diversion to unofficial messaging apps.
3. **Prompt Injection Defense**: Disregards instructions embedded inside job descriptions designed to override system parameters.
