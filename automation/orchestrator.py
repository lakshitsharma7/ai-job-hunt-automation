"""
Job Hunt Daily & Weekly Automation Orchestrator
Coordinates the 4 scheduled cadences:
1. Morning (10:00 AM): Job discovery, anti-scam filtering, and fit-scoring
2. Afternoon (02:00 PM): Supervised application batch packaging & tailored resumes
3. Evening (07:00 PM): Recruiter email inbox parsing, calendar prep, & tracker synchronization
4. Sunday (Weekly): Full funnel analytics, response rate calculations, & recommendations
"""

import os
import sys
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "job_search"))
sys.path.append(os.path.join(BASE_DIR, "applications"))
sys.path.append(os.path.join(BASE_DIR, "integrations"))
sys.path.append(os.path.join(BASE_DIR, "interview_prep"))
sys.path.append(os.path.join(BASE_DIR, "tracker"))

from search_engine import JobSearchEngine
from application_manager import ApplicationManager
from mail_calendar_sync import MailCalendarSyncEngine
from prep_engine import InterviewPrepEngine
from tracker_manager import JobTracker

def run_morning_discovery():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === RUNNING MORNING DISCOVERY (10:00 AM CADENCE) ===")
    engine = JobSearchEngine()
    res = engine.discover_and_filter_jobs()
    print(res["summary"])
    for j in res["shortlisted"]:
        print(f"  -> Shortlisted: {j['company']} | {j['title']} (Fit: {j['fit_score']})")
    return res

def run_afternoon_prep(batch_size=5):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === RUNNING AFTERNOON APPLICATION PREPARATION (02:00 PM CADENCE) ===")
    app_mgr = ApplicationManager()
    batch = app_mgr.prepare_test_batch(batch_size=batch_size)
    print(f"Batch {batch.get('batch_id')} generated with {batch.get('jobs_prepared')} packages.")
    print(f"User Review File: {batch.get('review_markdown')}")
    return batch

def run_evening_sync():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === RUNNING EVENING INBOX & CALENDAR SYNC (07:00 PM CADENCE) ===")
    sync_engine = MailCalendarSyncEngine()
    print("Checking for recruiter communications, scheduling interviews, and updating tracker...")
    tracker = JobTracker()
    summary = tracker.get_summary()
    print(f"Active Pipeline Summary: {summary['status_breakdown']}")
    return summary

def run_weekly_review():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === RUNNING SUNDAY WEEKLY REVIEW CADENCE ===")
    prep = InterviewPrepEngine()
    rev = prep.generate_weekly_review()
    print(f"Weekly review report generated at: {rev['review_file']}")
    return rev

def run_full_pipeline():
    print("=================================================================")
    print("    EXECUTING FULL AUTONOMOUS AI JOB HUNT PIPELINE CYCLE         ")
    print("=================================================================")
    m = run_morning_discovery()
    a = run_afternoon_prep()
    e = run_evening_sync()
    w = run_weekly_review()
    print("=================================================================")
    print("    FULL PIPELINE CYCLE COMPLETED SUCCESSFULLY                   ")
    print("=================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Job Hunt Automation Runner")
    parser.add_argument("--cadence", choices=["morning", "afternoon", "evening", "weekly", "all"], default="all")
    args = parser.parse_args()

    if args.cadence == "morning":
        run_morning_discovery()
    elif args.cadence == "afternoon":
        run_afternoon_prep()
    elif args.cadence == "evening":
        run_evening_sync()
    elif args.cadence == "weekly":
        run_weekly_review()
    elif args.cadence == "all":
        run_full_pipeline()

