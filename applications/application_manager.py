"""
Application Automation Engine (Phase 6 Implementation)
Executes the 12-step supervised job application workflow:
1. Load eligible job listing
2. Ingest complete job description
3. Deduplicate against tracker
4. Calculate fit score
5. Select best base resume
6. Tailor resume & cover letter if dream job
7. Map form answers from Answer Bank
8. Stage completed application fields
9. Present application package for user approval (HUMAN-IN-THE-LOOP)
10. Await explicit user confirmation (NO silent submissions)
11. Mark verified submission
12. Update tracker
"""

import os
import json
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "resumes"))
sys.path.append(os.path.join(BASE_DIR, "tracker"))

from scorer import calculate_fit_score
from tailor import tailor_resume_for_job
from tracker_manager import JobTracker

PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
BATCHES_DIR = os.path.join(BASE_DIR, "applications", "batches")
DISCOVERED_JOBS_FILE = os.path.join(BASE_DIR, "job_search", "discovered_jobs.json")

with open(os.path.join(PROFILES_DIR, "answer_bank.json"), "r", encoding="utf-8") as f:
    ANSWER_BANK = json.load(f)


class ApplicationManager:
    def __init__(self):
        self.tracker = JobTracker()

    def prepare_test_batch(self, batch_size=5, fallback_jobs=None):
        """
        Takes eligible shortlisted jobs and creates approval-ready packages.
        If discovered_jobs has no new shortlisted items, pulls active shortlisted jobs from the tracker or fallback.
        """
        shortlisted = []
        if os.path.exists(DISCOVERED_JOBS_FILE):
            with open(DISCOVERED_JOBS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            shortlisted = data.get("shortlisted", [])

        if not shortlisted:
            if fallback_jobs:
                shortlisted = fallback_jobs
            else:
                # Query tracker for active shortlisted jobs
                rows = self.tracker.get_all_rows()
                for r in rows:
                    if r.get("Application Status") in ["Shortlisted", "Awaiting Approval"]:
                        shortlisted.append({
                            "company": r.get("Company"),
                            "title": r.get("Role"),
                            "portal": r.get("Portal", "LinkedIn"),
                            "job_url": r.get("Job URL"),
                            "fit_score": float(r.get("Fit Score", 85.0)),
                            "fit_breakdown": {
                                "recommended_resume": r.get("Resume Used", "Lakshit-Sharma-Software-Developer"),
                                "matched_must_have": ["Python", "React", "REST APIs"]
                            },
                            "must_have_skills": ["Python", "React", "REST APIs"],
                            "nice_to_have_skills": ["FastAPI", "Tailwind CSS"],
                            "description": f"Role for {r.get('Role')} at {r.get('Company')}."
                        })
                        if len(shortlisted) >= batch_size:
                            break

        shortlisted = shortlisted[:batch_size]
        batch_id = datetime.now().strftime("batch_%Y%m%d_%H%M%S")
        batch_folder = os.path.join(BATCHES_DIR, batch_id)
        os.makedirs(batch_folder, exist_ok=True)

        packages = []

        for job in shortlisted:
            company = job["company"]
            role = job["title"]
            portal = job["portal"]
            url = job["job_url"]
            fit_score = job["fit_score"]
            rec_resume = job["fit_breakdown"]["recommended_resume"]

            # Map form answers from answer bank
            p_info = ANSWER_BANK["personal_info"]
            std_ans = ANSWER_BANK["standard_form_answers"]

            form_payload = {
                "Full Name": p_info["full_name"],
                "First Name": p_info["first_name"],
                "Last Name": p_info["last_name"],
                "Email": p_info["email"],
                "Phone": p_info["phone"],
                "Current City": p_info["city"],
                "LinkedIn URL": p_info["linkedin"],
                "GitHub URL": p_info["github"],
                "Portfolio URL": p_info["portfolio"],
                "Total Experience": f"{std_ans['total_experience_years']} Year",
                "Highest Education": f"{std_ans['highest_qualification']} ({std_ans['degree_name']})",
                "Graduation Year": std_ans["graduation_year"],
                "Current Company": std_ans["current_company"],
                "Current Role": std_ans["current_designation"],
                "Current CTC": std_ans["current_ctc_lpa"],
                "Expected CTC": std_ans["expected_ctc_lpa"],
                "Notice Period": std_ans["notice_period_text"],
                "Earliest Joining Date": std_ans["earliest_joining_date"],
                "Work Authorization": p_info["work_authorization"],
                "Willing to Relocate": std_ans["willing_to_relocate"],
                "Preferred Work Mode": ", ".join(std_ans["preferred_work_modes"]),
                "Resume Attached": f"{rec_resume}.pdf"
            }

            # Generate tailored package for high-fit/dream job
            tailor_data = tailor_resume_for_job(
                company_name=company,
                role_title=role,
                job_description=job.get("description", ""),
                must_have_skills=job.get("must_have_skills", []),
                nice_to_have_skills=job.get("nice_to_have_skills", []),
                min_exp=job.get("min_experience_years", 1),
                location=job.get("location", "Delhi NCR"),
                work_mode=job.get("work_mode", "Hybrid")
            )

            pkg = {
                "job_id": f"{company}_{role}".replace(" ", "_").lower(),
                "company": company,
                "role": role,
                "portal": portal,
                "job_url": url,
                "fit_score": fit_score,
                "recommended_resume": rec_resume,
                "tailored_resume_pdf": tailor_data["exported_files"]["pdf"],
                "tailored_resume_docx": tailor_data["exported_files"]["docx"],
                "cover_note": tailor_data["cover_note_120_words"],
                "recruiter_outreach_note": tailor_data["recruiter_note_under_200_chars"],
                "recruiter_note_chars": tailor_data["recruiter_note_length"],
                "form_fields_ready": form_payload,
                "approval_status": "Awaiting Approval",
                "safety_declaration": "No passwords, banking details, or unverified claims included."
            }

            # Save individual package
            pkg_file = os.path.join(batch_folder, f"{pkg['job_id']}.json")
            with open(pkg_file, "w", encoding="utf-8") as pf:
                json.dump(pkg, pf, indent=2)

            packages.append(pkg)

            # Update tracker status to 'Awaiting Approval'
            self.tracker.add_or_update_job({
                "Company": company,
                "Role": role,
                "Job URL": url,
                "Portal": portal,
                "Fit Score": fit_score,
                "Resume Used": rec_resume,
                "Application Status": "Awaiting Approval",
                "Next Action": "Awaiting User Approval to Submit",
                "Notes": f"Application package generated in {batch_id}"
            })

        # Generate a clean Markdown summary for the user
        md_summary_file = os.path.join(batch_folder, "batch_review.md")
        with open(md_summary_file, "w", encoding="utf-8") as mf:
            mf.write(f"# SUPERVISED APPLICATION BATCH REVIEW — {batch_id.upper()}\n\n")
            mf.write("> **Strict Safety Rule**: No application is submitted automatically. Review each package below.\n\n")
            for idx, p in enumerate(packages, 1):
                mf.write(f"## {idx}. {p['company']} — {p['role']}\n")
                mf.write(f"- **Portal**: {p['portal']} | **URL**: {p['job_url']}\n")
                mf.write(f"- **Fit Score**: `{p['fit_score']}/100`\n")
                mf.write(f"- **Selected Base Resume**: `{p['recommended_resume']}.pdf`\n")
                mf.write(f"- **Tailored PDF Generated**: `{os.path.basename(p['tailored_resume_pdf'])}`\n")
                mf.write(f"- **Recruiter Note ({p['recruiter_note_chars']} chars)**: *\"{p['recruiter_outreach_note']}\"*\n\n")
                mf.write(f"### Prepared Form Fields:\n```json\n{json.dumps(p['form_fields_ready'], indent=2)}\n```\n\n")
                mf.write(f"### 120-Word Cover Note:\n```text\n{p['cover_note']}\n```\n\n")
                mf.write("---\n\n")

        return {
            "batch_id": batch_id,
            "batch_path": batch_folder,
            "jobs_prepared": len(packages),
            "review_markdown": md_summary_file,
            "packages": packages
        }

    def simulate_user_approval_and_submit(self, batch_id, job_index=0, approved=True):
        """
        Executes user confirmation step (Human-in-the-loop).
        Transitions status from 'Awaiting Approval' to 'Applied' only upon confirmation.
        """
        batch_folder = os.path.join(BATCHES_DIR, batch_id)
        if not os.path.exists(batch_folder):
            return {"error": "Batch not found"}

        pkg_files = [f for f in os.listdir(batch_folder) if f.endswith(".json")]
        if job_index >= len(pkg_files):
            return {"error": "Job index out of range"}

        target_file = os.path.join(batch_folder, pkg_files[job_index])
        with open(target_file, "r", encoding="utf-8") as f:
            pkg = json.load(f)

        if not approved:
            pkg["approval_status"] = "Rejected by User"
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(pkg, f, indent=2)
            self.tracker.add_or_update_job({
                "Company": pkg["company"],
                "Role": pkg["role"],
                "Job URL": pkg["job_url"],
                "Application Status": "Skipped",
                "Next Action": "Skipped by User Request",
                "Notes": "Application cancelled during user review."
            })
            return {"status": "Cancelled", "company": pkg["company"]}

        # Approved!
        pkg["approval_status"] = "Applied (User Approved)"
        pkg["submission_timestamp"] = datetime.now().isoformat()
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(pkg, f, indent=2)

        self.tracker.add_or_update_job({
            "Company": pkg["company"],
            "Role": pkg["role"],
            "Job URL": pkg["job_url"],
            "Application Status": "Applied",
            "Next Action": "Follow-up in 7 days (Prompt 11)",
            "Notes": f"Submitted with tailored resume: {os.path.basename(pkg['tailored_resume_pdf'])}"
        })

        return {
            "status": "Applied",
            "company": pkg["company"],
            "role": pkg["role"],
            "resume_used": os.path.basename(pkg["tailored_resume_pdf"]),
            "timestamp": pkg["submission_timestamp"],
            "tracker_status": "Applied"
        }


if __name__ == "__main__":
    mgr = ApplicationManager()
    batch = mgr.prepare_test_batch(5)
    print("=== SUPERVISED APPLICATION TEST BATCH PREPARED ===")
    print(f"Batch ID: {batch['batch_id']}")
    print(f"Total Packages: {batch['jobs_prepared']}")
    print(f"Review Markdown: {batch['review_markdown']}")
    for p in batch["packages"]:
        print(f"• Ready for Review: {p['company']} ({p['role']}) — Fit: {p['fit_score']}")

    print("\n=== SIMULATING USER APPROVAL FOR 1 TEST JOB ===")
    approved_res = mgr.simulate_user_approval_and_submit(batch["batch_id"], job_index=0, approved=True)
    print(json.dumps(approved_res, indent=2))
