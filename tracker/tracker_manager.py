"""
Job Hunt Tracker Manager
Maintains both Job_Hunt_Tracker.xlsx (formatted Excel) and Job_Hunt_Tracker.csv.
Enforces schema validation, status lifecycles, and duplicate detection.
"""

import os
import csv
import json
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKER_DIR = os.path.join(BASE_DIR, "tracker")
XLSX_PATH = os.path.join(TRACKER_DIR, "Job_Hunt_Tracker.xlsx")
CSV_PATH = os.path.join(TRACKER_DIR, "Job_Hunt_Tracker.csv")

COLUMNS = [
    "Date",
    "Company",
    "Role",
    "Job URL",
    "Portal",
    "Location",
    "Fit Score",
    "Resume Used",
    "Application Status",
    "Recruiter",
    "Next Action",
    "Notes"
]

VALID_STATUSES = [
    "Discovered",
    "Shortlisted",
    "Awaiting Approval",
    "Applied",
    "Recruiter Reply",
    "Interview Scheduled",
    "Interview Completed",
    "Rejected",
    "Offer Received",
    "Skipped"
]

STATUS_COLORS = {
    "Applied": "D4EDDA",              # Soft green
    "Interview Scheduled": "CCE5FF",   # Soft blue
    "Interview Completed": "D1ECF1",   # Cyan
    "Offer Received": "D1E7DD",        # Mint green
    "Recruiter Reply": "FFF3CD",       # Soft yellow
    "Shortlisted": "E2E3E5",           # Light grey
    "Awaiting Approval": "FFEBAA",     # Amber
    "Rejected": "F8D7DA",              # Soft red
    "Skipped": "E9ECEF",               # Grey
    "Discovered": "FFFFFF"             # White
}


class JobTracker:
    def __init__(self, xlsx_path=XLSX_PATH, csv_path=CSV_PATH):
        self.xlsx_path = xlsx_path
        self.csv_path = csv_path
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(os.path.dirname(self.xlsx_path), exist_ok=True)
        
        # Ensure CSV
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(COLUMNS)

        # Ensure XLSX
        if not os.path.exists(self.xlsx_path):
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Job Hunt Tracker"
            
            # Header styling
            header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
            header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
            header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

            ws.append(COLUMNS)
            ws.row_dimensions[1].height = 26

            for col_idx, col_name in enumerate(COLUMNS, 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_align
                ws.column_dimensions[get_column_letter(col_idx)].width = max(len(col_name) + 5, 14)

            # Freeze top row
            ws.freeze_panes = "A2"
            wb.save(self.xlsx_path)

    def get_all_rows(self):
        rows = []
        if os.path.exists(self.csv_path):
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    rows.append(r)
        return rows

    def is_already_applied_or_tracked(self, job_url, company=None, role=None):
        clean_url = job_url.strip().lower().split("?")[0] if job_url else ""
        for r in self.get_all_rows():
            existing_url = r.get("Job URL", "").strip().lower().split("?")[0]
            if clean_url and existing_url == clean_url:
                return True, r.get("Application Status", "Unknown")
            if company and role:
                if (r.get("Company", "").strip().lower() == company.strip().lower() and 
                    r.get("Role", "").strip().lower() == role.strip().lower()):
                    return True, r.get("Application Status", "Unknown")
        return False, None

    def add_or_update_job(self, entry):
        """
        entry dict should contain keys matching COLUMNS or subsets.
        """
        # Validate status
        status = entry.get("Application Status", "Discovered")
        if status not in VALID_STATUSES:
            status = "Discovered"
        entry["Application Status"] = status

        if "Date" not in entry or not entry["Date"]:
            entry["Date"] = datetime.now().strftime("%Y-%m-%d")

        existing_rows = self.get_all_rows()
        updated = False
        target_url = entry.get("Job URL", "").strip().lower().split("?")[0]

        for i, row in enumerate(existing_rows):
            cur_url = row.get("Job URL", "").strip().lower().split("?")[0]
            if target_url and cur_url == target_url:
                for k in COLUMNS:
                    if k in entry and entry[k] is not None:
                        existing_rows[i][k] = str(entry[k])
                updated = True
                break

        if not updated:
            new_row = {col: str(entry.get(col, "")) for col in COLUMNS}
            existing_rows.append(new_row)

        # Write back to CSV
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(existing_rows)

        # Write back to XLSX
        self._sync_xlsx(existing_rows)
        return "Updated" if updated else "Added"

    def _sync_xlsx(self, rows):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Job Hunt Tracker"

        header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
        header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        ws.append(COLUMNS)
        ws.row_dimensions[1].height = 24
        for col_idx in range(1, len(COLUMNS) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align

        thin_border = Border(
            left=Side(style='thin', color='DDDDDD'),
            right=Side(style='thin', color='DDDDDD'),
            top=Side(style='thin', color='DDDDDD'),
            bottom=Side(style='thin', color='DDDDDD')
        )

        for row_idx, r in enumerate(rows, start=2):
            row_data = [r.get(c, "") for c in COLUMNS]
            ws.append(row_data)
            ws.row_dimensions[row_idx].height = 20
            status = r.get("Application Status", "")
            fill_color = STATUS_COLORS.get(status, "FFFFFF")
            row_fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")

            for col_idx in range(1, len(COLUMNS) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = Font(name="Arial", size=9)
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")
                if col_idx in [1, 5, 7, 9]: # Centered columns (Date, Portal, Fit Score, Status)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                if col_idx == 9 and fill_color != "FFFFFF": # Colorize Status cell
                    cell.fill = row_fill
                    cell.font = Font(name="Arial", size=9, bold=True)

        for col_idx, col_name in enumerate(COLUMNS, 1):
            max_len = max([len(str(r.get(col_name, ""))) for r in rows] + [len(col_name)])
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_len + 3, 12), 40)

        ws.freeze_panes = "A2"
        wb.save(self.xlsx_path)

    def get_summary(self):
        rows = self.get_all_rows()
        counts = {}
        for r in rows:
            s = r.get("Application Status", "Discovered")
            counts[s] = counts.get(s, 0) + 1
        return {
            "total_jobs": len(rows),
            "status_breakdown": counts
        }


if __name__ == "__main__":
    tracker = JobTracker()
    test_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Company": "TechNova Solutions",
        "Role": "Junior Frontend Engineer (React)",
        "Job URL": "https://linkedin.com/jobs/view/10001",
        "Portal": "LinkedIn",
        "Location": "Noida, India",
        "Fit Score": 95.0,
        "Resume Used": "Lakshit-Sharma-Frontend-Developer",
        "Application Status": "Applied",
        "Recruiter": "Priya Sharma",
        "Next Action": "Follow-up in 7 days",
        "Notes": "Applied with tailored 1-page resume"
    }
    action = tracker.add_or_update_job(test_entry)
    print("Action:", action)
    print("Summary:", tracker.get_summary())

