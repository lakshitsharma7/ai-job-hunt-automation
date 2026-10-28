"""
Fit-Score Calculation Engine
Calculates job fit score (0-100) using the exact formula from the Claude Job Hunt Setup Guide:
- Must-have skills: 50%
- Experience level: 20%
- Location / work mode: 15%
- Nice-to-have skills: 15%
Threshold: Skip jobs below 60.
"""

import re
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")

with open(os.path.join(PROFILES_DIR, "answer_bank.json"), "r", encoding="utf-8") as f:
    ANSWER_BANK = json.load(f)

with open(os.path.join(PROFILES_DIR, "job_preferences.json"), "r", encoding="utf-8") as f:
    JOB_PREFERENCES = json.load(f)

# Candidate verified attributes
CANDIDATE_SKILLS = set([s.lower() for s in ANSWER_BANK["skill_experience_years"].keys()] + [
    "react", "react.js", "javascript", "python", "fastapi", "django", "rest api", "rest apis",
    "html", "css", "html5", "css3", "tailwind", "tailwind css", "next.js", "nextjs",
    "postgresql", "postgres", "sql", "n8n", "ai", "genai", "generative ai", "llm", "ai agents",
    "pyside6", "git", "github", "power bi", "pandas", "numpy", "jenkins", "ci/cd", "pyinstaller"
])

CANDIDATE_EXP_YEARS = float(ANSWER_BANK["standard_form_answers"]["total_experience_years"]) # 1.0 (junior/entry)
CANDIDATE_LOCATIONS = set([l.lower() for l in JOB_PREFERENCES["location_preferences"]["primary_cities"] + 
                          JOB_PREFERENCES["location_preferences"]["relocation_cities"] + 
                          ["remote", "hybrid", "delhi", "delhi ncr", "noida", "gurugram", "gurgaon", "bangalore", "bengaluru", "pune", "hyderabad", "india"]])


def calculate_fit_score(job_data):
    """
    Evaluates job_data dictionary containing:
    - title: str
    - description: str
    - required_skills / must_have_skills: list
    - nice_to_have_skills: list
    - min_experience_years: float or int
    - location: str
    - work_mode: str ('remote', 'hybrid', 'on-site')
    """
    must_have = [s.strip().lower() for s in job_data.get("must_have_skills", [])]
    nice_to_have = [s.strip().lower() for s in job_data.get("nice_to_have_skills", [])]
    min_exp = float(job_data.get("min_experience_years", 0))
    location = job_data.get("location", "").lower()
    work_mode = job_data.get("work_mode", "").lower()

    # 1. Must-have skills (50%)
    if must_have:
        matched_must = [s for s in must_have if any(cs in s or s in cs for cs in CANDIDATE_SKILLS)]
        missing_must = [s for s in must_have if s not in matched_must]
        must_score = (len(matched_must) / len(must_have)) * 50.0
    else:
        matched_must = []
        missing_must = []
        must_score = 45.0 # fallback when not specified

    # 2. Experience level (20%)
    # Candidate has 1 yr + 2 yrs projects, ideal for 0-2 yrs
    if min_exp <= 2.0:
        exp_score = 20.0
    elif min_exp <= 3.0:
        exp_score = 14.0 # Stretch
    else:
        exp_score = 5.0  # Over senior

    # 3. Location / Work mode (15%)
    loc_matched = False
    if "remote" in work_mode or "remote" in location:
        loc_score = 15.0
        loc_matched = True
    elif any(loc in location for loc in CANDIDATE_LOCATIONS):
        loc_score = 15.0
        loc_matched = True
    else:
        loc_score = 5.0 # Unpreferred or international location

    # 4. Nice-to-have skills (15%)
    if nice_to_have:
        matched_nice = [s for s in nice_to_have if any(cs in s or s in cs for cs in CANDIDATE_SKILLS)]
        missing_nice = [s for s in nice_to_have if s not in matched_nice]
        nice_score = (len(matched_nice) / len(nice_to_have)) * 15.0
    else:
        matched_nice = []
        missing_nice = []
        nice_score = 12.0

    total_score = round(must_score + exp_score + loc_score + nice_score, 1)
    eligible = total_score >= 60.0

    # Auto-detect best base resume
    title_lower = job_data.get("title", "").lower()
    desc_lower = job_data.get("description", "").lower()
    
    if any(k in title_lower for k in ["react", "frontend", "ui", "web developer"]):
        best_resume = "Lakshit-Sharma-Frontend-Developer"
    elif any(k in title_lower for k in ["python", "backend", "fastapi", "django"]):
        best_resume = "Lakshit-Sharma-Python-Developer"
    elif any(k in title_lower for k in ["ai", "automation", "llm", "agent", "workflow"]):
        best_resume = "Lakshit-Sharma-AI-Automation-Developer"
    else:
        best_resume = "Lakshit-Sharma-Software-Developer"

    return {
        "fit_score": total_score,
        "eligible": eligible,
        "recommended_resume": best_resume,
        "score_breakdown": {
            "must_have_skills_points": round(must_score, 1),
            "experience_level_points": round(exp_score, 1),
            "location_work_mode_points": round(loc_score, 1),
            "nice_to_have_skills_points": round(nice_score, 1)
        },
        "matched_must_have": matched_must,
        "missing_must_have": missing_must,
        "matched_nice_to_have": matched_nice,
        "missing_nice_to_have": nice_nice if (nice_nice := missing_nice) else [],
        "reason": f"Scored {total_score}/100. Matched {len(matched_must)}/{len(must_have)} must-haves. Exp req {min_exp} yrs compatible. Location '{location or work_mode}' aligned."
    }


if __name__ == "__main__":
    sample_job = {
        "title": "Junior Frontend Engineer (React)",
        "company": "TechNova Solutions",
        "location": "Noida, India",
        "work_mode": "Hybrid",
        "min_experience_years": 1,
        "must_have_skills": ["React", "JavaScript", "HTML5", "CSS3", "REST APIs"],
        "nice_to_have_skills": ["Next.js", "Tailwind CSS", "TypeScript"],
        "description": "Looking for a Junior Frontend Developer to build modern React interfaces and integrate RESTful APIs."
    }
    res = calculate_fit_score(sample_job)
    print(json.dumps(res, indent=2))

