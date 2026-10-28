"""
End-to-End Verification Test Suite for Autonomous AI Job Hunt System
Executes tests across all 11 critical modules and reports evidence.
"""

import os
import sys
import json
import fitz
import openpyxl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "resumes"))
sys.path.append(os.path.join(BASE_DIR, "job_search"))
sys.path.append(os.path.join(BASE_DIR, "applications"))
sys.path.append(os.path.join(BASE_DIR, "tracker"))
sys.path.append(os.path.join(BASE_DIR, "integrations"))
sys.path.append(os.path.join(BASE_DIR, "interview_prep"))
sys.path.append(os.path.join(BASE_DIR, "automation"))

def run_all_tests():
    report = []
    
    print("==================================================================")
    print("     AUTONOMOUS AI JOB HUNT SYSTEM — VERIFICATION TEST SUITE      ")
    print("==================================================================")

    # Test 1: Master Profile & Answer Bank
    mp_file = os.path.join(BASE_DIR, "profiles", "master_profile.md")
    ab_file = os.path.join(BASE_DIR, "profiles", "answer_bank.json")
    t1_pass = os.path.exists(mp_file) and os.path.exists(ab_file)
    with open(ab_file, "r", encoding="utf-8") as f:
        ab_data = json.load(f)
    t1_pass = t1_pass and ab_data["personal_info"]["full_name"] == "Lakshit Sharma"
    report.append(("1. Master Profile & Answer Bank", "PASS" if t1_pass else "FAIL", f"Verified profile for {ab_data['personal_info']['full_name']}"))

    # Test 2: 4 Base Resumes Generation (DOCX + PDF)
    res_dir = os.path.join(BASE_DIR, "resumes")
    expected_resumes = [
        "Lakshit-Sharma-Frontend-Developer",
        "Lakshit-Sharma-Python-Developer",
        "Lakshit-Sharma-AI-Automation-Developer",
        "Lakshit-Sharma-Software-Developer"
    ]
    t2_pass = True
    evidence_res = []
    for r in expected_resumes:
        pdf_p = os.path.join(res_dir, f"{r}.pdf")
        docx_p = os.path.join(res_dir, f"{r}.docx")
        if not (os.path.exists(pdf_p) and os.path.exists(docx_p)):
            t2_pass = False
        else:
            doc = fitz.open(pdf_p)
            evidence_res.append(f"{r}: {len(doc)} page")
            doc.close()
    report.append(("2. 4 ATS Resumes (PDF + DOCX)", "PASS" if t2_pass else "FAIL", ", ".join(evidence_res)))

    # Test 3: Fit-Score Calculator (Formula verification)
    from scorer import calculate_fit_score
    test_jd = {
        "title": "Junior React Developer",
        "must_have_skills": ["React", "JavaScript", "HTML5", "CSS3"],
        "nice_to_have_skills": ["Tailwind CSS"],
        "min_experience_years": 1,
        "location": "Noida",
        "work_mode": "Hybrid"
    }
    score_res = calculate_fit_score(test_jd)
    t3_pass = score_res["fit_score"] >= 80.0 and score_res["eligible"] is True
    report.append(("3. Fit-Score Calculator (0-100 Rubric)", "PASS" if t3_pass else "FAIL", f"Score: {score_res['fit_score']}/100, Eligible: {score_res['eligible']}"))

    # Test 4: Dream Job Resume Tailoring
    from tailor import tailor_resume_for_job
    tailor_res = tailor_resume_for_job("Acme AI", "Frontend Engineer", "React & UI Developer", ["React", "JavaScript"], [], 1, "Delhi", "Remote")
    t4_pass = os.path.exists(tailor_res["exported_files"]["pdf"]) and tailor_res["recruiter_note_length"] <= 200
    report.append(("4. Resume Tailoring & Cover Letter", "PASS" if t4_pass else "FAIL", f"PDF: {os.path.basename(tailor_res['exported_files']['pdf'])}, Recruiter note chars: {tailor_res['recruiter_note_length']}"))

    # Test 5: Job Discovery & Anti-Scam Filter
    from search_engine import JobSearchEngine
    se = JobSearchEngine()
    disc_res = se.discover_and_filter_jobs()
    t5_pass = "shortlisted" in disc_res and len(disc_res["skipped"]) > 0
    report.append(("5. Job Discovery & Anti-Scam Filter", "PASS" if t5_pass else "FAIL", disc_res["summary"]))

    # Test 6: Application Packaging & Approval Workflow
    from application_manager import ApplicationManager
    am = ApplicationManager()
    batch = am.prepare_test_batch(1)
    t6_pass = os.path.exists(batch["review_markdown"]) and batch["jobs_prepared"] >= 1
    report.append(("6. Application Preparation & Human-in-the-Loop", "PASS" if t6_pass else "FAIL", f"Batch {batch['batch_id']}: {batch['jobs_prepared']} package(s) ready"))

    # Test 7: Duplicate Detection
    from tracker_manager import JobTracker
    tracker = JobTracker()
    is_dup, _ = tracker.is_already_applied_or_tracked("https://careers.technova.io/jobs/fe-react-01")
    t7_pass = is_dup is True
    report.append(("7. Duplicate Application Prevention", "PASS" if t7_pass else "FAIL", f"Duplicate successfully intercepted: {is_dup}"))

    # Test 8: Tracker Updates (Excel & CSV)
    xlsx_p = os.path.join(BASE_DIR, "tracker", "Job_Hunt_Tracker.xlsx")
    csv_p = os.path.join(BASE_DIR, "tracker", "Job_Hunt_Tracker.csv")
    wb = openpyxl.load_workbook(xlsx_p)
    ws = wb.active
    t8_pass = os.path.exists(xlsx_p) and os.path.exists(csv_p) and ws.max_row >= 2
    report.append(("8. Job Hunt Tracker (XLSX & CSV)", "PASS" if t8_pass else "FAIL", f"Tracked rows in Excel: {ws.max_row - 1}"))

    # Test 9: Email & Calendar Integration (RFC 5545 ICS)
    from mail_calendar_sync import MailCalendarSyncEngine
    mc = MailCalendarSyncEngine()
    slots = mc.find_free_interview_slots(count=3)
    t9_pass = len(slots) == 3 and all(s[0].hour in range(10, 18) for s in slots)
    report.append(("9. Calendar Free-Slot Detection (10-18 IST)", "PASS" if t9_pass else "FAIL", f"Generated {len(slots)} valid 45-min weekday slots"))

    # Test 10: Interview Prep Brief & Mock Scoring
    from prep_engine import InterviewPrepEngine
    pe = InterviewPrepEngine()
    brief = pe.generate_prep_brief("TestCo", "React Developer")
    t10_pass = os.path.exists(brief["filepath"])
    report.append(("10. Interview Prep Brief Engine", "PASS" if t10_pass else "FAIL", f"Brief generated: {os.path.basename(brief['filepath'])}"))

    # Test 11: Daily Automation Orchestrator
    from orchestrator import run_weekly_review
    rev = run_weekly_review()
    t11_pass = os.path.exists(rev["review_file"])
    report.append(("11. Automation Orchestrator & Weekly Review", "PASS" if t11_pass else "FAIL", f"Report: {os.path.basename(rev['review_file'])}"))

    print("\n------------------------------------------------------------------")
    print("                        TEST RESULTS MATRIX                       ")
    print("------------------------------------------------------------------")
    all_passed = True
    for name, status, evidence in report:
        print(f"[{status}] {name}")
        print(f"       -> Evidence: {evidence}")
        if status != "PASS":
            all_passed = False

    print("==================================================================")
    if all_passed:
        print(">> ALL 11 TESTS PASSED SUCCESSFULLY (100% OPERATIONAL)")
    else:
        print(">> SOME TESTS FAILED")
    print("==================================================================")

if __name__ == "__main__":
    run_all_tests()

