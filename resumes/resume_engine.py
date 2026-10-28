"""
ATS-Friendly Resume Generation Engine for Lakshit Sharma
Generates clean single-column ATS-compliant resumes in both DOCX and PDF formats.
Strictly uses verified information from master_profile.md.
"""

import os
import json
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Load answer bank and job preferences
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
OUTPUT_DIR = os.path.join(BASE_DIR, "resumes")

with open(os.path.join(PROFILES_DIR, "answer_bank.json"), "r", encoding="utf-8") as f:
    ANSWER_BANK = json.load(f)

CONTACT_INFO = {
    "name": "LAKSHIT SHARMA",
    "contact_line": "North East Delhi, India | +91 9910933221 | lakshitharitash@gmail.com",
    "links_line": "Portfolio: lakshitsharma7.github.io | GitHub: github.com/lakshitsharma7 | LinkedIn: linkedin.com/in/lakshit-sharma-448949289"
}

ROLE_CONFIGS = {
    "frontend": {
        "title": "Frontend Developer",
        "file_suffix": "Frontend-Developer",
        "tagline": "Software Engineer — Frontend & React.js Specialist",
        "summary": "Software Engineer with hands-on experience building performant, responsive web applications and interactive client interfaces using React.js, Next.js, JavaScript, and Tailwind CSS. Proven track record developing candidate management dashboards, component libraries, and REST API integrations with rigorous error handling and clean component architecture.",
        "skills": {
            "Languages & Core": "JavaScript (ES6+), TypeScript, HTML5, CSS3, SQL, Python",
            "Frontend Frameworks": "React.js, Next.js, Vite, Tailwind CSS, Redux, Component Architecture",
            "APIs & Integration": "REST APIs, Webhooks, JSON, Postman, Fetch / Axios, Client-Side Caching",
            "Tools & Workflows": "Git, GitHub, VS Code, Figma, Responsive UI Design, CI/CD, Testing"
        },
        "highlight_projects": ["ta-ats", "workpulse", "portfolio_3d"],
        "experience_focus": "frontend"
    },
    "python": {
        "title": "Python Developer",
        "file_suffix": "Python-Developer",
        "tagline": "Software Engineer — Python, FastAPI, Django & Desktop Telemetry",
        "summary": "Software Engineer with deep hands-on expertise building production REST APIs, telemetry systems, and backend services using Python, FastAPI, Django, and PostgreSQL. Experienced architecting multi-threaded desktop applications with local-first persistent queuing, zero data loss telemetry, dynamic device token authentication, and automated CI/CD packaging.",
        "skills": {
            "Programming Languages": "Python, SQL, JavaScript (ES6+), HTML5, CSS3",
            "Backend Frameworks": "FastAPI, Django, REST APIs, Webhooks, Microservices, JWT, RBAC",
            "Databases & ORM": "PostgreSQL, SQLite, SQL, SQLAlchemy, Peewee",
            "Desktop & System": "PySide6 (Qt for Python), PyInstaller, Multi-threading, Windows & macOS Builds",
            "DevOps & Tools": "Git, GitHub, Jenkins CI/CD, Postman, Docker, Linux / Windows"
        },
        "highlight_projects": ["workpulse", "ta-ats", "ai_automation"],
        "experience_focus": "python"
    },
    "ai_automation": {
        "title": "AI Automation Developer",
        "file_suffix": "AI-Automation-Developer",
        "tagline": "AI Automation Engineer — LLM Integration, n8n Workflows & API Pipelines",
        "summary": "Software Engineer specializing in AI automation workflows, LLM application pipelines, and API integrations. Experienced orchestrating event-driven automation in n8n and Python, integrating Generative AI APIs, structured prompt engineering, and building resilient webhooks for enterprise data routing and automated task execution.",
        "skills": {
            "AI & GenAI": "Generative AI, AI APIs, Prompt Engineering, AI Agents, LLM Integration, Model Context Protocol (MCP)",
            "Automation & Integration": "n8n, Workflow Automation, Webhooks, REST APIs, JSON Processing, Event Routing",
            "Backend Engineering": "Python, FastAPI, Django, PostgreSQL, Asynchronous Pipelines",
            "Data & Tools": "SQL, Pandas, Postman, Git, GitHub, Rapid Prototyping"
        },
        "highlight_projects": ["ai_automation", "ta-ats", "workpulse"],
        "experience_focus": "automation"
    },
    "software_dev": {
        "title": "Software Developer",
        "file_suffix": "Software-Developer",
        "tagline": "Software Developer — Full-Stack Engineering, Python, React & REST APIs",
        "summary": "Software Engineer with comprehensive experience across full-stack application development, backend REST APIs, client frontend interfaces, and cross-platform desktop telemetry. Hands-on proficiency with Python, FastAPI, Django, React.js, Next.js, and PostgreSQL, with a demonstrated focus on architectural resilience, automated testing, and CI/CD pipelines.",
        "skills": {
            "Programming": "Python, JavaScript, SQL, HTML5, CSS3",
            "Full-Stack": "React.js, Next.js, FastAPI, Django, REST APIs, Tailwind CSS",
            "Databases & Storage": "PostgreSQL, SQLite, SQL (Window Functions, CTEs)",
            "Systems & DevOps": "PySide6, Git, GitHub, Jenkins CI/CD, PyInstaller, Postman",
            "Engineering Practices": "Authentication, RBAC, Error Handling, Telemetry, Agile Workflows"
        },
        "highlight_projects": ["workpulse", "ta-ats", "customer_churn"],
        "experience_focus": "fullstack"
    }
}

PROJECTS_DATA = {
    "workpulse": {
        "title": "Workpulse — AI-Assisted Employee Productivity Platform",
        "tech": "Python, PySide6, REST APIs, PostgreSQL, Windows, macOS, PyInstaller",
        "bullets": [
            "Developed a cross-platform desktop productivity monitoring application for employee activity tracking.",
            "Implemented application/session tracking, active and idle time calculation, screenshots and system-health monitoring.",
            "Built local-first activity processing with backend synchronization and configurable batch uploads.",
            "Integrated device enrollment, dynamic device tokens, authentication and API-driven configuration.",
            "Implemented automatic startup, tracking-resume and application update/version-management workflows.",
            "Packaged native installers for Windows (.exe) and macOS (.dmg) with automated Jenkins CI/CD pipelines."
        ]
    },
    "ta-ats": {
        "title": "TA-ATS — AI-Powered Talent Acquisition Platform",
        "tech": "Next.js, React, FastAPI, Django, PostgreSQL, AI, MCP, Tailwind CSS",
        "bullets": [
            "Developed an Applicant Tracking System for recruitment workflows and candidate information management.",
            "Built frontend modules using Next.js, React and Tailwind CSS and backend services using Django and FastAPI.",
            "Implemented role-based access workflows for recruiters, candidates, hiring managers, project managers and administrators.",
            "Developed recruitment workflow states including Draft -> Pending Approval -> Approved -> Published.",
            "Integrated AI-assisted candidate evaluation and dynamic API-driven dashboard workflows."
        ]
    },
    "ai_automation": {
        "title": "AI Automation & Workflow Projects",
        "tech": "n8n, REST APIs, Webhooks, AI APIs, Python, JSON, AI Agents",
        "bullets": [
            "Built AI-assisted automation workflows connecting APIs, webhooks, and enterprise applications.",
            "Orchestrated event-driven workflows, multi-step JSON transformations, and conditional branching logic in n8n.",
            "Integrated AI model endpoints for automated text classification, data enrichment, and intelligent response generation.",
            "Implemented robust error-handling hooks and retry mechanisms across asynchronous third-party API pipelines."
        ]
    },
    "customer_churn": {
        "title": "CloudSync — Customer Churn & Retention Analytics",
        "tech": "Power BI, DAX, Python, SQL, Pandas, Scikit-Learn, PostgreSQL",
        "bullets": [
            "Analyzed $17.04M ARR and 12,000 accounts (210,000+ telemetry rows) to identify enterprise churn drivers.",
            "Engineered Star Schema data model and authored 20 analytical SQL queries using Window Functions and CTEs.",
            "Designed 6-page interactive Power BI executive dashboard with dynamic DAX metrics and customer risk scoring.",
            "Trained Random Forest classification model achieving 0.98 ROC-AUC for early-warning churn risk intervention."
        ]
    },
    "portfolio_3d": {
        "title": "3D Interactive Developer Portfolio",
        "tech": "React, TypeScript, Three.js, Vite, Tailwind CSS",
        "bullets": [
            "Engineered an interactive 3D WebGL developer portfolio featuring fluid Three.js scene animations and responsive controls.",
            "Integrated custom virtual AI Assistant guide with quick-prompt actions and contextual navigation.",
            "Optimized asset rendering and shader computations to achieve 60 FPS performance across desktop and mobile browsers."
        ]
    }
}


def create_docx_resume(role_key, filepath):
    conf = ROLE_CONFIGS[role_key]
    doc = Document()
    
    # 0.5 in margins for maximum content fit on single page
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.55)
        section.right_margin = Inches(0.55)
        section.different_first_page_header_footer = False

    # Helper styling functions
    def add_heading_rule(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text.upper())
        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0, 51, 102) # Classic navy
        
        # Add bottom border XML
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '003366')
        pBdr.append(bottom)
        pPr.append(pBdr)

    # 1. Header
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(1)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_run = title_p.add_run(CONTACT_INFO["name"])
    name_run.bold = True
    name_run.font.name = "Arial"
    name_run.font.size = Pt(16)
    name_run.font.color.rgb = RGBColor(20, 20, 20)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(2)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run(conf["tagline"])
    sub_run.bold = True
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(9.5)
    sub_run.font.color.rgb = RGBColor(0, 51, 102)

    c_p = doc.add_paragraph()
    c_p.paragraph_format.space_before = Pt(0)
    c_p.paragraph_format.space_after = Pt(1)
    c_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c_run = c_p.add_run(CONTACT_INFO["contact_line"])
    c_run.font.name = "Arial"
    c_run.font.size = Pt(8.5)

    l_p = doc.add_paragraph()
    l_p.paragraph_format.space_before = Pt(0)
    l_p.paragraph_format.space_after = Pt(4)
    l_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    l_run = l_p.add_run(CONTACT_INFO["links_line"])
    l_run.font.name = "Arial"
    l_run.font.size = Pt(8.5)

    # 2. Professional Summary
    add_heading_rule("Professional Summary")
    sum_p = doc.add_paragraph()
    sum_p.paragraph_format.space_before = Pt(2)
    sum_p.paragraph_format.space_after = Pt(4)
    sum_p.paragraph_format.line_spacing = 1.15
    sum_run = sum_p.add_run(conf["summary"])
    sum_run.font.name = "Arial"
    sum_run.font.size = Pt(9.0)

    # 3. Technical Skills
    add_heading_rule("Technical Skills")
    for category, skills in conf["skills"].items():
        sk_p = doc.add_paragraph()
        sk_p.paragraph_format.space_before = Pt(1)
        sk_p.paragraph_format.space_after = Pt(1)
        sk_p.paragraph_format.line_spacing = 1.1
        cat_run = sk_p.add_run(f"• {category}: ")
        cat_run.bold = True
        cat_run.font.name = "Arial"
        cat_run.font.size = Pt(8.5)
        val_run = sk_p.add_run(skills)
        val_run.font.name = "Arial"
        val_run.font.size = Pt(8.5)

    # 4. Professional Experience
    add_heading_rule("Professional Experience")
    
    # Indovision Services
    exp_p1 = doc.add_paragraph()
    exp_p1.paragraph_format.space_before = Pt(3)
    exp_p1.paragraph_format.space_after = Pt(1)
    r1 = exp_p1.add_run("Software Engineer Intern | Indovision Services")
    r1.bold = True
    r1.font.name = "Arial"
    r1.font.size = Pt(9.0)
    r2 = exp_p1.add_run("  —  Apr 2026 – Present | India")
    r2.italic = True
    r2.font.name = "Arial"
    r2.font.size = Pt(8.5)

    indovision_bullets = [
        "Develop and maintain software applications using Python, FastAPI, Django, React, Next.js and PostgreSQL.",
        "Build and integrate multiple REST APIs and backend functions for authentication, device registration, activity tracking, attendance, tasks, screenshots, synchronization and application management.",
        "Develop Workpulse, a cross-platform employee productivity monitoring application using Python and PySide6 with local-first activity persistence.",
        "Implement activity/session tracking, active/idle time calculation, system-health collection, and dynamic device tokens.",
        "Build Windows and macOS application packaging workflows using PyInstaller, Windows installers, and macOS DMG builds.",
        "Set up Jenkins CI/CD pipelines to automate application build, testing, and deployment workflows."
    ]
    for b in indovision_bullets:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_before = Pt(0)
        bp.paragraph_format.space_after = Pt(1.5)
        bp.paragraph_format.line_spacing = 1.05
        brun = bp.add_run(b)
        brun.font.name = "Arial"
        brun.font.size = Pt(8.5)

    # Nexen Bloom
    exp_p2 = doc.add_paragraph()
    exp_p2.paragraph_format.space_before = Pt(3)
    exp_p2.paragraph_format.space_after = Pt(1)
    nr1 = exp_p2.add_run("Data Analytics Intern | Nexen Bloom")
    nr1.bold = True
    nr1.font.name = "Arial"
    nr1.font.size = Pt(9.0)
    nr2 = exp_p2.add_run("  —  Feb 2026 – Apr 2026 | Noida, India")
    nr2.italic = True
    nr2.font.name = "Arial"
    nr2.font.size = Pt(8.5)

    nexen_bullets = [
        "Worked with Python, Pandas, NumPy, SQL, and Power BI for data cleaning, transformation, and business KPI reporting.",
        "Built interactive executive dashboards to communicate operational metrics and authored SQL queries for data aggregation."
    ]
    for b in nexen_bullets:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_before = Pt(0)
        bp.paragraph_format.space_after = Pt(1.5)
        bp.paragraph_format.line_spacing = 1.05
        brun = bp.add_run(b)
        brun.font.name = "Arial"
        brun.font.size = Pt(8.5)

    # 5. Key Projects
    add_heading_rule("Key Projects")
    for pkey in conf["highlight_projects"]:
        pdata = PROJECTS_DATA[pkey]
        proj_hdr = doc.add_paragraph()
        proj_hdr.paragraph_format.space_before = Pt(2.5)
        proj_hdr.paragraph_format.space_after = Pt(1)
        pr1 = proj_hdr.add_run(pdata["title"])
        pr1.bold = True
        pr1.font.name = "Arial"
        pr1.font.size = Pt(9.0)
        pr2 = proj_hdr.add_run(f" | {pdata['tech']}")
        pr2.italic = True
        pr2.font.name = "Arial"
        pr2.font.size = Pt(8.0)

        for b in pdata["bullets"][:3]:  # Top 3 most relevant bullets
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_before = Pt(0)
            bp.paragraph_format.space_after = Pt(1)
            bp.paragraph_format.line_spacing = 1.05
            brun = bp.add_run(b)
            brun.font.name = "Arial"
            brun.font.size = Pt(8.5)

    # 6. Education & Certifications
    add_heading_rule("Education & Certifications")
    edu_p = doc.add_paragraph()
    edu_p.paragraph_format.space_before = Pt(2)
    edu_p.paragraph_format.space_after = Pt(1)
    er1 = edu_p.add_run("Bachelor of Technology (B.Tech) — Computer Science & Engineering")
    er1.bold = True
    er1.font.name = "Arial"
    er1.font.size = Pt(9.0)
    er2 = edu_p.add_run(" | Krishna Engineering College (AKTU), 2021 – 2025")
    er2.font.name = "Arial"
    er2.font.size = Pt(8.5)

    cert_p = doc.add_paragraph()
    cert_p.paragraph_format.space_before = Pt(1)
    cert_p.paragraph_format.space_after = Pt(2)
    crun = cert_p.add_run("Certifications: Power BI for Beginners (Microsoft/Simplilearn) • Python & JS Bootcamps (NSDC/ITM) • SQL Basics (Newton School) • Front-end Internship (IBM SkillsBuild)")
    crun.font.name = "Arial"
    crun.font.size = Pt(8.0)

    doc.save(filepath)
    return filepath


def create_pdf_resume(role_key, filepath):
    conf = ROLE_CONFIGS[role_key]
    doc = fitz.open()
    
    # A4 dimensions: 595.28 x 841.89 points
    page_w, page_h = 595.28, 841.89
    margin_x = 36.0  # 0.5 in
    margin_top = 36.0
    margin_bottom = 36.0
    content_w = page_w - (2 * margin_x)
    
    page = doc.new_page(width=page_w, height=page_h)
    
    y = margin_top
    
    # Header: Name
    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 20)
    page.insert_textbox(rect, CONTACT_INFO["name"], fontsize=15, fontname="helv", fontfile=None, align=1)
    y += 20
    
    # Header: Tagline
    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 13)
    page.insert_textbox(rect, conf["tagline"], fontsize=9.5, fontname="times-bold", align=1)
    y += 14
    
    # Header: Contact Info
    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 11)
    page.insert_textbox(rect, CONTACT_INFO["contact_line"], fontsize=8.2, fontname="helv", align=1)
    y += 11

    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 11)
    page.insert_textbox(rect, CONTACT_INFO["links_line"], fontsize=8.2, fontname="helv", align=1)
    y += 15

    def draw_section_header(title, cur_y):
        rect = fitz.Rect(margin_x, cur_y, page_w - margin_x, cur_y + 13)
        page.insert_textbox(rect, title.upper(), fontsize=9.5, fontname="helv", align=0)
        # Navy accent rule line
        line_y = cur_y + 13
        p1 = fitz.Point(margin_x, line_y)
        p2 = fitz.Point(page_w - margin_x, line_y)
        page.draw_line(p1, p2, color=(0.0, 0.2, 0.4), width=0.8)
        return line_y + 4

    # Summary
    y = draw_section_header("Professional Summary", y)
    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 36)
    page.insert_textbox(rect, conf["summary"], fontsize=8.2, fontname="helv", align=3)
    y += 38

    # Technical Skills
    y = draw_section_header("Technical Skills", y)
    for cat, skl in conf["skills"].items():
        rect = fitz.Rect(margin_x + 6, y, page_w - margin_x, y + 11)
        text = f"•  {cat}: {skl}"
        page.insert_textbox(rect, text, fontsize=7.8, fontname="helv", align=0)
        y += 11.5
    y += 3

    # Experience
    y = draw_section_header("Professional Experience", y)
    
    # Indovision
    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 12)
    page.insert_textbox(rect, "Software Engineer Intern — Indovision Services | Apr 2026 – Present", fontsize=8.5, fontname="helv", align=0)
    y += 12
    indovision_bullets = [
        "Develop and maintain software applications using Python, FastAPI, Django, React, Next.js and PostgreSQL.",
        "Build and integrate multiple REST APIs and backend functions for authentication, device registration, activity tracking, attendance, tasks, screenshots, synchronization and application management.",
        "Develop Workpulse, a cross-platform employee productivity monitoring application using Python and PySide6.",
        "Implement activity/session tracking, active and idle time calculation, screenshots and system-health monitoring.",
        "Build Windows and macOS application packaging workflows using PyInstaller, Windows installers and macOS DMG builds.",
        "Set up Jenkins CI/CD pipelines to automate application build, testing and deployment workflows."
    ]
    for b in indovision_bullets:
        rect = fitz.Rect(margin_x + 8, y, page_w - margin_x, y + 18)
        page.insert_textbox(rect, f"•  {b}", fontsize=7.6, fontname="helv", align=0)
        y += 11.5
    y += 3

    # Nexen Bloom
    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 12)
    page.insert_textbox(rect, "Data Analytics Intern — Nexen Bloom, Noida | Feb 2026 – Apr 2026", fontsize=8.5, fontname="helv", align=0)
    y += 12
    nexen_bullets = [
        "Worked with Python, Pandas, NumPy, SQL and Power BI for data cleaning, transformation, and business reporting.",
        "Built executive KPI dashboards and used SQL for data extraction, filtering, aggregation and operational reporting."
    ]
    for b in nexen_bullets:
        rect = fitz.Rect(margin_x + 8, y, page_w - margin_x, y + 18)
        page.insert_textbox(rect, f"•  {b}", fontsize=7.6, fontname="helv", align=0)
        y += 11.5
    y += 3

    # Projects
    y = draw_section_header("Key Projects", y)
    for pkey in conf["highlight_projects"]:
        pdata = PROJECTS_DATA[pkey]
        rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 11)
        page.insert_textbox(rect, f"{pdata['title']} | {pdata['tech']}", fontsize=8.2, fontname="helv", align=0)
        y += 11
        for b in pdata["bullets"][:3]:
            rect = fitz.Rect(margin_x + 8, y, page_w - margin_x, y + 18)
            page.insert_textbox(rect, f"•  {b}", fontsize=7.5, fontname="helv", align=0)
            y += 10.5
        y += 2

    # Education & Certifications
    y = draw_section_header("Education & Certifications", y)
    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 11)
    page.insert_textbox(rect, "B.Tech in Computer Science & Engineering — Krishna Engineering College (AKTU) | 2021 – 2025", fontsize=8.0, fontname="helv", align=0)
    y += 11.5

    rect = fitz.Rect(margin_x, y, page_w - margin_x, y + 11)
    page.insert_textbox(rect, "Certifications: Power BI for Beginners (Microsoft/Simplilearn) • Python & JS Bootcamps (NSDC/ITM) • SQL Basics (Newton School)", fontsize=7.5, fontname="helv", align=0)
    y += 11

    doc.save(filepath)
    doc.close()
    return filepath


def generate_all():
    generated_files = []
    for role_key, conf in ROLE_CONFIGS.items():
        base_name = f"Lakshit-Sharma-{conf['file_suffix']}"
        docx_path = os.path.join(OUTPUT_DIR, f"{base_name}.docx")
        pdf_path = os.path.join(OUTPUT_DIR, f"{base_name}.pdf")
        
        create_docx_resume(role_key, docx_path)
        create_pdf_resume(role_key, pdf_path)
        
        generated_files.append((docx_path, pdf_path))
        print(f"Generated: {base_name}.docx and {base_name}.pdf")
    return generated_files


if __name__ == "__main__":
    generate_all()

