# AI Job Hunt Automation System

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python)](https://www.python.org/)
[![ATS](https://img.shields.io/badge/ATS%20Compatibility-100%25%20Single--Column-green)](https://github.com/lakshitsharma7/ai-job-hunt-automation)
[![Architecture](https://img.shields.io/badge/Architecture-Autonomous%20Agentic%20Pipeline-orange)](https://github.com/lakshitsharma7/ai-job-hunt-automation)
[![Security](https://img.shields.io/badge/Security-Zero--PII%20Gated-red)](https://github.com/lakshitsharma7/ai-job-hunt-automation)

> **Autonomous AI-powered job search automation system for intelligent job matching, ATS resume tailoring, application tracking, and interview preparation using Python and AI agents.**

Adapted from advanced autonomous job hunt methodologies into an enterprise-grade, local-first Python architecture with strict **human-in-the-loop** safety guardrails.

---

## 🌟 Key Capabilities

- **Intelligent 0–100 Fit-Score Rubric**:
  Evaluates every job description against verified candidate credentials using exact weighting:
  - *Must-Have Skills*: 50%
  - *Experience Level Alignment*: 20%
  - *Location & Work Mode*: 15%
  - *Nice-to-Have Skills*: 15%
  - *Threshold*: Automatically filters out positions scoring below 60.
- **ATS-Friendly Resume Generation Engine**:
  Generates single-column vector PDFs (`PyMuPDF`) and Word documents (`python-docx`) without tables, text boxes, or graphics, guaranteed to fit on exactly 1 page.
- **Dream-Job Resume Tailoring**:
  Re-synthesizes candidate summaries and top bullets into the prospective employer's vocabulary using 100% verified facts, alongside a 120-word tailored cover note and recruiter outreach (<200 characters).
- **Automated Anti-Scam & Safety Filter**:
  Detects and blacklists suspicious listings demanding security deposits, equipment training fees, or diversion to private messaging platforms (Telegram/WhatsApp).
- **Supervised Application Packaging (Human-in-the-Loop)**:
  Prepares approval-ready application packages in daily batches with structured form payloads and markdown review cards. **Zero silent submissions**.
- **Formatted Spreadsheet Tracker**:
  Maintains both [`Job_Hunt_Tracker.xlsx`](tracker/) and CSV databases with 12 standardized columns and conditional status color-coding.
- **Recruiter Email & Calendar Sync**:
  Detects interview invitations, finds 3 free 45-minute weekday slots (10:00–18:00 IST), prepares interview `.ics` calendar events with automated 30-minute pre-interview preparation blocks, and drafts response emails.
- **Full Interview Preparation Suite**:
  Generates 1-page company research briefs, tailored 60-second self-introductions, 8 targeted technical/HR questions with answer outlines, 1–10 mock scoring, post-call debriefs, and 7-day follow-up outreach.

---

## 📂 Project Architecture

```text
ai-job-hunt-automation/
├── automation/                    # Automated schedulers & one-click runners
│   ├── orchestrator.py            # Master automation runner CLI
│   ├── run_morning.ps1            # 10:00 AM Discovery runner
│   ├── run_afternoon.ps1          # 02:00 PM Application Packaging runner
│   ├── run_evening.ps1            # 07:00 PM Recruiter & Calendar sync runner
│   ├── run_weekly.ps1             # Sunday weekly analytics runner
│   └── run_all.ps1                # Full-cycle test execution runner
│
├── applications/                  # Supervised application packaging & approval
│   ├── application_manager.py     # 12-step application package generator
│   └── batches/                   # Timestamped approval packages & review cards
│
├── config/                        # Operational rules & workflow mappings
│   ├── rules.md                   # Operational guardrails (zero-fabrication)
│   └── workflow_mapping.md        # 10-Step & 12-Prompt mapping specifications
│
├── docs/                          # Developer documentation
│   └── SETUP.md                   # Complete installation & configuration guide
│
├── integrations/                  # Email, Calendar, and Google Sheets connectors
│   ├── mail_calendar_sync.py      # Recruiter email parser & RFC 5545 ICS calendar generator
│   └── gsheets_sync.py            # Live Google Sheets synchronization connector
│
├── interview_prep/                # Interview preparation & practice suite
│   ├── prep_engine.py             # Brief generator, mock interview evaluator, debriefs
│   └── weekly_review.md           # Sunday application funnel conversion review
│
├── job_search/                    # Multi-portal discovery & scam protection
│   ├── search_engine.py           # Discovery engine with anti-scam & duplicate detection
│   └── discovered_jobs.json       # Normalized listings with fit scoring
│
├── profiles/                      # Ground truth candidate data & preferences
│   ├── master_profile.example.md  # Template master profile
│   ├── answer_bank.example.json   # Template standardized application answers
│   └── job_preferences.example.json # Role, location, and compensation preferences
│
├── resumes/                       # ATS resume generators & tailored output files
│   ├── resume_engine.py           # Single-column ATS DOCX & PDF generation engine
│   ├── scorer.py                  # Fit score calculation engine (0-100 rubric)
│   └── tailor.py                  # Dream-job resume tailoring & cover letter engine
│
├── tracker/                       # Master application audit log & funnel tracker
│   ├── tracker_manager.py         # OpenPyXL & CSV management engine
│   └── Job_Hunt_Tracker.example.csv # Sample tracking database
│
├── .env.example                   # Environment variable template
├── .gitignore                     # Strict privacy & secret exclusions
├── README.md                      # Project documentation
├── requirements.txt               # Production dependencies
├── run.bat                        # Windows interactive terminal menu
└── test_system.py                 # 11-step end-to-end verification test suite
```

---

## ⚡ Quick Start

### 1. Installation
```bash
git clone https://github.com/lakshitsharma7/ai-job-hunt-automation.git
cd ai-job-hunt-automation
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure Ground Truth
Copy template files in `profiles/` and populate your verified details:
```bash
cp profiles/master_profile.example.md profiles/master_profile.md
cp profiles/answer_bank.example.json profiles/answer_bank.json
cp profiles/job_preferences.example.json profiles/job_preferences.json
```

### 3. Generate Your ATS Resumes
```bash
python resumes/resume_engine.py
```

### 4. Run the Full Daily Cycle
- **On Windows**: Double-click `run.bat` or run:
  ```powershell
  python automation/orchestrator.py --cadence all
  ```

---

## 📅 Daily Automation Cadence

| Time | Stage | Action | Command |
| :--- | :--- | :--- | :--- |
| **10:00 AM** | **Morning Discovery** | Scans permitted portals, filters scams, calculates fit score ($\ge 60$), checks duplicates. | `python automation/orchestrator.py --cadence morning` |
| **02:00 PM** | **Application Prep** | Prepares approval packages, selects base resume, generates tailored dream resumes. | `python automation/orchestrator.py --cadence afternoon` |
| **07:00 PM** | **Inbox & Calendar Sync**| Checks recruiter replies, finds 45-min slots, prepares `.ics` calendar events with prep blocks. | `python automation/orchestrator.py --cadence evening` |
| **Sunday** | **Weekly Review** | Analyzes portal conversion funnel, response rates, and generates optimization recommendations. | `python automation/orchestrator.py --cadence weekly` |

---

## 🛡️ Security, Privacy & Ethics Guardrails

- **Zero Fabrication**: Every bullet point and metric originates exclusively from verified ground truth records.
- **Privacy Gated**: Personal contact details, private answer banks, and submitted batch history are strictly excluded by `.gitignore`.
- **No Stored Passwords**: Automation never stores, asks for, or types passwords, OTPs, or government identity numbers.
- **Platform Compliance**: Respects rate limits, portal terms of service, and anti-bot rules; all submissions require human confirmation.

---

## 🧪 Verification & Testing

Verify that all 11 core sub-systems and scoring calculators operate with 100% pass status:
```bash
python test_system.py
```

---

## 📄 License

*Subject to candidate confirmation (e.g. MIT License).*
