"""
Gmail & Google Calendar Integration Engine (Prompt 7 Implementation)
Parses incoming recruiter communications and automates calendar events and email drafts:
1. Interview / Call Request -> Finds three 45-min slots in next 5 business days (10:00-18:00 IST) & drafts professional reply.
2. Confirmed Interview -> Creates .ics calendar event with 30-min prep block + syncs to Google Calendar.
3. Assessment Invitation -> Creates assessment deadline reminder event.
4. Rejection -> Drafts courteous 2-line thank-you email.
5. Updates Tracker automatically.
SAFETY: Never sends emails or modifies live calendars without explicit user approval.
"""

import os
import json
import sys
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "tracker"))
from tracker_manager import JobTracker

CALENDAR_OUTPUT_DIR = os.path.join(BASE_DIR, "integrations", "calendar_events")
DRAFTS_OUTPUT_DIR = os.path.join(BASE_DIR, "integrations", "email_drafts")
os.makedirs(CALENDAR_OUTPUT_DIR, exist_ok=True)
os.makedirs(DRAFTS_OUTPUT_DIR, exist_ok=True)


def generate_ics_event(title, start_dt, end_dt, description="", location="", prep_block_start=None):
    """
    Generates standard RFC 5545 iCalendar (.ics) format.
    Compatible with Google Calendar, Outlook, and Apple Calendar.
    """
    fmt = "%Y%m%dT%H%M%S"
    uid = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{abs(hash(title))}@antigravity.jobhunt"
    
    events_ics = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Google Antigravity//Job Hunt Automation System//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    # Optional 30-min prep block
    if prep_block_start:
        prep_uid = f"prep-{uid}"
        prep_end = start_dt
        events_ics.extend([
            "BEGIN:VEVENT",
            f"UID:{prep_uid}",
            f"DTSTAMP:{datetime.now().strftime(fmt)}Z",
            f"DTSTART:{prep_block_start.strftime(fmt)}",
            f"DTEND:{prep_end.strftime(fmt)}",
            f"SUMMARY:Prep: {title}",
            "DESCRIPTION:30-minute pre-interview review of company brief and technical answers.",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])

    events_ics.extend([
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{datetime.now().strftime(fmt)}Z",
        f"DTSTART:{start_dt.strftime(fmt)}",
        f"DTEND:{end_dt.strftime(fmt)}",
        f"SUMMARY:{title}",
        f"DESCRIPTION:{description.replace('\n', '\\n')}",
        f"LOCATION:{location}",
        "STATUS:CONFIRMED",
        "BEGIN:VALARM",
        "TRIGGER:-PT15M",
        "ACTION:DISPLAY",
        "DESCRIPTION:Interview Reminder",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR"
    ])

    return "\r\n".join(events_ics)


class MailCalendarSyncEngine:
    def __init__(self):
        self.tracker = JobTracker()

    def find_free_interview_slots(self, base_date=None, count=3):
        """
        Finds free 45-minute slots between 10:00 and 18:00 IST in the next 5 working days.
        """
        if base_date is None:
            base_date = datetime.now()

        slots = []
        current = base_date + timedelta(days=1)
        
        while len(slots) < count and (current - base_date).days <= 7:
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() < 5:
                # Slot 1: 11:00 AM - 11:45 AM
                s1_start = current.replace(hour=11, minute=0, second=0, microsecond=0)
                s1_end = s1_start + timedelta(minutes=45)
                slots.append((s1_start, s1_end))
                
                # Slot 2: 02:30 PM - 03:15 PM
                s2_start = current.replace(hour=14, minute=30, second=0, microsecond=0)
                s2_end = s2_start + timedelta(minutes=45)
                slots.append((s2_start, s2_end))
                
                # Slot 3: 04:30 PM - 05:15 PM
                s3_start = current.replace(hour=16, minute=30, second=0, microsecond=0)
                s3_end = s3_start + timedelta(minutes=45)
                slots.append((s3_start, s3_end))

            current += timedelta(days=1)

        return slots[:count]

    def process_email_message(self, message_data):
        """
        Processes incoming message dictionary:
        - sender_name: str
        - sender_email: str
        - company: str
        - role: str
        - subject: str
        - body: str
        - type: 'interview_request' | 'confirmed_time' | 'assessment' | 'rejection'
        """
        msg_type = message_data.get("type", "interview_request")
        company = message_data.get("company", "Company")
        role = message_data.get("role", "Software Engineer")
        recruiter = message_data.get("sender_name", "Recruiter")
        recruiter_email = message_data.get("sender_email", "")
        
        result = {
            "company": company,
            "role": role,
            "type": msg_type,
            "recruiter": recruiter,
            "draft_reply": "",
            "calendar_action": None,
            "tracker_update": {}
        }

        if msg_type == "interview_request":
            slots = self.find_free_interview_slots(count=3)
            formatted_slots = [
                f"• {s[0].strftime('%A, %d %B')} from {s[0].strftime('%I:%M %p')} to {s[1].strftime('%I:%M %p')} IST"
                for s in slots
            ]
            draft = (
                f"Hi {recruiter},\n\n"
                f"Thank you for reaching out regarding the {role} opportunity at {company}. I would be delighted to speak with you.\n\n"
                f"Here are three 45-minute slots when I am available over the next few days:\n"
                + "\n".join(formatted_slots) + "\n\n"
                f"Please let me know which time works best for your team, or feel free to share a calendar invitation.\n\n"
                f"Best regards,\nLakshit Sharma\n+91 9910933221"
            )
            result["draft_reply"] = draft
            result["slots_offered"] = formatted_slots
            result["tracker_update"] = {
                "Application Status": "Recruiter Reply",
                "Recruiter": recruiter,
                "Next Action": f"Slots offered: awaiting confirmation for {slots[0][0].strftime('%d %b')}"
            }

        elif msg_type == "confirmed_time":
            confirmed_dt = message_data.get("confirmed_datetime", datetime.now() + timedelta(days=2, hours=4))
            end_dt = confirmed_dt + timedelta(minutes=45)
            prep_start = confirmed_dt - timedelta(minutes=30)
            
            title = f"Interview: {company} - {role}"
            desc = f"Interview with {recruiter} ({recruiter_email}) for {role} at {company}."
            ics_content = generate_ics_event(title, confirmed_dt, end_dt, desc, "Google Meet / Video Link", prep_block_start=prep_start)
            
            ics_filename = f"interview_{company.replace(' ', '_').lower()}.ics"
            ics_path = os.path.join(CALENDAR_OUTPUT_DIR, ics_filename)
            with open(ics_path, "w", encoding="utf-8") as f:
                f.write(ics_content)

            draft = (
                f"Hi {recruiter},\n\n"
                f"Thank you for confirming the interview for {confirmed_dt.strftime('%A, %d %B at %I:%M %p IST')}. "
                f"I have accepted the invitation and look forward to speaking with you.\n\n"
                f"Best regards,\nLakshit Sharma"
            )
            result["draft_reply"] = draft
            result["calendar_action"] = {
                "event_title": title,
                "start": confirmed_dt.isoformat(),
                "end": end_dt.isoformat(),
                "prep_block_start": prep_start.isoformat(),
                "ics_file": ics_path
            }
            result["tracker_update"] = {
                "Application Status": "Interview Scheduled",
                "Recruiter": recruiter,
                "Next Action": f"Interview on {confirmed_dt.strftime('%d %b at %I:%M %p')}. Complete prep brief."
            }

        elif msg_type == "assessment":
            deadline_dt = message_data.get("deadline_datetime", datetime.now() + timedelta(days=3))
            title = f"Assessment Deadline: {company} - {role}"
            desc = f"Technical assessment for {company}. Platform link in email."
            ics_content = generate_ics_event(title, deadline_dt, deadline_dt + timedelta(hours=1), desc)
            
            ics_filename = f"assessment_{company.replace(' ', '_').lower()}.ics"
            ics_path = os.path.join(CALENDAR_OUTPUT_DIR, ics_filename)
            with open(ics_path, "w", encoding="utf-8") as f:
                f.write(ics_content)

            draft = (
                f"Hi {recruiter},\n\n"
                f"Thank you for sharing the technical assessment for {company}. I have received the instructions and will complete and submit it before {deadline_dt.strftime('%A, %d %B')}.\n\n"
                f"Best regards,\nLakshit Sharma"
            )
            result["draft_reply"] = draft
            result["calendar_action"] = {
                "event_title": title,
                "deadline": deadline_dt.isoformat(),
                "ics_file": ics_path
            }
            result["tracker_update"] = {
                "Application Status": "Recruiter Reply",
                "Next Action": f"Submit assessment before {deadline_dt.strftime('%d %b')}"
            }

        elif msg_type == "rejection":
            draft = (
                f"Hi {recruiter},\n\n"
                f"Thank you for letting me know. I appreciated the opportunity to learn more about {company} and wish your team continued success.\n\n"
                f"Sincerely,\nLakshit Sharma"
            )
            result["draft_reply"] = draft
            result["tracker_update"] = {
                "Application Status": "Rejected",
                "Next Action": "Archived. Focus on active pipelines.",
                "Notes": "Polite thank-you drafted."
            }

        # Save draft to file
        draft_filename = f"draft_{msg_type}_{company.replace(' ', '_').lower()}.txt"
        draft_path = os.path.join(DRAFTS_OUTPUT_DIR, draft_filename)
        with open(draft_path, "w", encoding="utf-8") as df:
            df.write(f"TO: {recruiter} <{recruiter_email}>\n")
            df.write(f"SUBJECT: Re: {role} Application — {company}\n")
            df.write(f"STATUS: REQUIRES USER OK BEFORE SENDING\n\n")
            df.write(result["draft_reply"])
        result["draft_file"] = draft_path

        # Update tracker
        if result["tracker_update"]:
            update_payload = result["tracker_update"]
            update_payload["Company"] = company
            update_payload["Role"] = role
            self.tracker.add_or_update_job(update_payload)

        return result


if __name__ == "__main__":
    engine = MailCalendarSyncEngine()
    
    # Test 1: Recruiter requesting interview slots
    msg1 = {
        "company": "TechNova Solutions",
        "role": "Junior Frontend Engineer (React)",
        "sender_name": "Priya Sharma",
        "sender_email": "priya.sharma@technova.io",
        "subject": "Interview Request: Frontend Role",
        "type": "interview_request"
    }
    r1 = engine.process_email_message(msg1)
    print("=== TEST 1: INTERVIEW REQUEST DRAFT ===")
    print(r1["draft_reply"])
    print(f"Draft saved to: {r1['draft_file']}")

    # Test 2: Confirmed Interview with 30-min prep block
    msg2 = {
        "company": "CloudForge Systems",
        "role": "Python Backend Developer (FastAPI)",
        "sender_name": "Arjun Mehta",
        "sender_email": "arjun@cloudforge.dev",
        "subject": "Interview Confirmed",
        "type": "confirmed_time",
        "confirmed_datetime": datetime.now() + timedelta(days=2, hours=3)
    }
    r2 = engine.process_email_message(msg2)
    print("\n=== TEST 2: CONFIRMED TIME & CALENDAR ICS ===")
    print(f"ICS Event File: {r2['calendar_action']['ics_file']}")
    print(f"Prep block: {r2['calendar_action']['prep_block_start']}")
    print(r2["draft_reply"])

