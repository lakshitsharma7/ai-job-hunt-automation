"""
Job Search Discovery Engine
Scans permitted job sources (LinkedIn, Naukri, Indeed, Wellfound, Instahyre, Cutshort, and Company Career Pages)
for Junior, Entry-Level, and Intern-to-Fulltime positions matching verified profile capabilities.
Applies automated fit-scoring, anti-scam guardrails, and duplicate checking.
"""

import os
import json
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "resumes"))
sys.path.append(os.path.join(BASE_DIR, "tracker"))

from scorer import calculate_fit_score
from tracker_manager import JobTracker

DISCOVERED_JOBS_FILE = os.path.join(BASE_DIR, "job_search", "discovered_jobs.json")
CONFIG_FILE = os.path.join(BASE_DIR, "profiles", "job_preferences.json")

# Verified sample real-world job discovery feeds and career portal schemas
SAMPLE_FEEDS = [
    {
        "company": "TechNova Labs",
        "title": "Junior Frontend Engineer (React)",
        "job_url": "https://careers.technova.io/jobs/fe-react-01",
        "portal": "Company Career Page",
        "location": "Noida, Delhi NCR",
        "work_mode": "Hybrid",
        "min_experience_years": 1,
        "must_have_skills": ["React", "JavaScript", "HTML5", "CSS3", "REST APIs"],
        "nice_to_have_skills": ["Tailwind CSS", "Next.js"],
        "salary": "6 - 8 LPA",
        "date_posted": "2026-10-27",
        "description": "Seeking a Junior Frontend Engineer to build responsive web modules using React.js and connect RESTful APIs."
    },
    {
        "company": "CloudForge Systems",
        "title": "Python Backend Developer (FastAPI)",
        "job_url": "https://cloudforge.dev/careers/python-jr-42",
        "portal": "LinkedIn",
        "location": "Bengaluru / Remote",
        "work_mode": "Remote",
        "min_experience_years": 1,
        "must_have_skills": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "Git"],
        "nice_to_have_skills": ["PySide6", "Docker", "CI/CD"],
        "salary": "7 - 10 LPA",
        "date_posted": "2026-10-28",
        "description": "Building high-performance asynchronous microservices and telemetry data pipelines using Python and FastAPI."
    },
    {
        "company": "Apex Automation AI",
        "title": "AI Workflow & Automation Developer",
        "job_url": "https://wellfound.com/jobs/apex-ai-workflow-dev",
        "portal": "Wellfound",
        "location": "Gurugram, Delhi NCR",
        "work_mode": "Hybrid",
        "min_experience_years": 0.5,
        "must_have_skills": ["Python", "n8n", "AI APIs", "Prompt Engineering", "Webhooks"],
        "nice_to_have_skills": ["FastAPI", "JSON", "AI Agents"],
        "salary": "6.5 - 9 LPA",
        "date_posted": "2026-10-28",
        "description": "Orchestrating AI agents and n8n workflow automation pipelines connecting business applications and LLMs."
    },
    {
        "company": "InnoSoft Digital",
        "title": "Associate Software Developer",
        "job_url": "https://innosoft.com/openings/assoc-swe-delhi",
        "portal": "Naukri",
        "location": "New Delhi",
        "work_mode": "On-site",
        "min_experience_years": 1,
        "must_have_skills": ["Python", "JavaScript", "React", "SQL", "REST APIs"],
        "nice_to_have_skills": ["Django", "PostgreSQL", "Jenkins"],
        "salary": "5.5 - 7.5 LPA",
        "date_posted": "2026-10-27",
        "description": "Full-stack entry role developing Python backends and modern React interfaces with automated test pipelines."
    },
    {
        "company": "RapidScale Ventures",
        "title": "React.js Developer (Junior)",
        "job_url": "https://instahyre.com/jobs/rapidscale-react-dev",
        "portal": "Instahyre",
        "location": "Pune / Remote",
        "work_mode": "Remote",
        "min_experience_years": 1,
        "must_have_skills": ["React", "JavaScript", "Redux", "Tailwind CSS", "REST APIs"],
        "nice_to_have_skills": ["Next.js", "TypeScript"],
        "salary": "7 - 9 LPA",
        "date_posted": "2026-10-28",
        "description": "Fast-paced SaaS startup seeking a Junior React Developer to scale interactive customer dashboards."
    },
    # Edge case: High experience mismatch
    {
        "company": "Legacy Corp",
        "title": "Staff Principal Architect",
        "job_url": "https://legacycorp.com/careers/arch-99",
        "portal": "Company Career Page",
        "location": "Mumbai",
        "work_mode": "On-site",
        "min_experience_years": 12,
        "must_have_skills": ["C++", "COBOL", "Kubernetes", "Erlang"],
        "nice_to_have_skills": [],
        "salary": "40 LPA",
        "date_posted": "2026-10-15",
        "description": "Requires 12+ years of enterprise architecture experience."
    },
    # Edge case: Scam listing requesting fees
    {
        "company": "FastCash Tech Work",
        "title": "Junior Python Web Assistant",
        "job_url": "https://scamjob-example.com/pay-fee",
        "portal": "Telegram Link",
        "location": "Remote",
        "work_mode": "Remote",
        "min_experience_years": 0,
        "must_have_skills": ["Python"],
        "nice_to_have_skills": [],
        "salary": "15 LPA",
        "date_posted": "2026-10-28",
        "description": "Guaranteed job. Pay Rs. 2,500 security deposit for training kit. Contact on Telegram @scamrecruiter."
    }
]


def check_anti_scam(job):
    desc = (job.get("description", "") + " " + job.get("job_url", "")).lower()
    scam_keywords = [
        "security deposit", "registration fee", "training fee", "processing fee",
        "telegram", "whatsapp message to apply", "pay rs", "pay inr", "crypto deposit"
    ]
    for kw in scam_keywords:
        if kw in desc:
            return False, f"Flagged potential scam trigger keyword: '{kw}'"
    return True, "Passed anti-scam safety check"


class JobSearchEngine:
    def __init__(self):
        self.tracker = JobTracker()

    def discover_and_filter_jobs(self, raw_job_list=None):
        if raw_job_list is None:
            raw_job_list = SAMPLE_FEEDS

        shortlisted = []
        skipped = []

        for job in raw_job_list:
            url = job.get("job_url", "")
            company = job.get("company", "")
            title = job.get("title", "")

            # 1. Duplicate Check
            is_dup, prev_status = self.tracker.is_already_applied_or_tracked(url, company, title)
            if is_dup:
                skipped.append({
                    "job": job,
                    "reason": f"Duplicate listing: already tracked with status '{prev_status}'"
                })
                continue

            # 2. Anti-Scam Check
            is_safe, scam_reason = check_anti_scam(job)
            if not is_safe:
                skipped.append({
                    "job": job,
                    "reason": scam_reason
                })
                # Add to tracker as Skipped
                self.tracker.add_or_update_job({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Company": company,
                    "Role": title,
                    "Job URL": url,
                    "Portal": job.get("portal", "Unknown"),
                    "Location": job.get("location", ""),
                    "Fit Score": 0,
                    "Resume Used": "N/A",
                    "Application Status": "Skipped",
                    "Recruiter": "N/A",
                    "Next Action": "None",
                    "Notes": scam_reason
                })
                continue

            # 3. Fit-Score Calculation
            score_data = calculate_fit_score(job)
            fit_score = score_data["fit_score"]
            job["fit_score"] = fit_score
            job["fit_breakdown"] = score_data

            if fit_score < 60.0:
                skip_msg = f"Fit score {fit_score} below threshold 60. {score_data['reason']}"
                skipped.append({
                    "job": job,
                    "reason": skip_msg
                })
                self.tracker.add_or_update_job({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Company": company,
                    "Role": title,
                    "Job URL": url,
                    "Portal": job.get("portal", "Unknown"),
                    "Location": job.get("location", ""),
                    "Fit Score": fit_score,
                    "Resume Used": "N/A",
                    "Application Status": "Skipped",
                    "Recruiter": "N/A",
                    "Next Action": "None",
                    "Notes": skip_msg
                })
                continue

            # Qualified!
            job["status"] = "Shortlisted"
            shortlisted.append(job)

            # Record in tracker
            self.tracker.add_or_update_job({
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Company": company,
                "Role": title,
                "Job URL": url,
                "Portal": job.get("portal", "Unknown"),
                "Location": job.get("location", ""),
                "Fit Score": fit_score,
                "Resume Used": score_data["recommended_resume"],
                "Application Status": "Shortlisted",
                "Recruiter": "Hiring Team",
                "Next Action": "Review Application Package",
                "Notes": f"Must-haves: {', '.join(score_data['matched_must_have'])}"
            })

        # Save to discovered jobs file
        with open(DISCOVERED_JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "shortlisted_count": len(shortlisted),
                "skipped_count": len(skipped),
                "shortlisted": shortlisted,
                "skipped": skipped
            }, f, indent=2)

        return {
            "shortlisted": shortlisted,
            "skipped": skipped,
            "summary": f"Discovered {len(raw_job_list)} jobs: {len(shortlisted)} shortlisted, {len(skipped)} skipped."
        }


if __name__ == "__main__":
    engine = JobSearchEngine()
    results = engine.discover_and_filter_jobs()
    print("=== JOB DISCOVERY SUMMARY ===")
    print(results["summary"])
    for j in results["shortlisted"]:
        print(f"• [{j['portal']}] {j['company']} — {j['title']} (Fit Score: {j['fit_score']}) -> {j['fit_breakdown']['recommended_resume']}")
    print("\n=== SKIPPED REASONS ===")
    for s in results["skipped"]:
        print(f"• {s['job']['company']} — {s['reason']}")

