#!/usr/bin/env python3
"""
Mimic: AI-Powered Meeting Value Estimator & Workback Plan Generator
Usage: python mimic.py <user_email>
"""

__version__ = "1.0.0"

import sys
import json
import time
import argparse
import requests
import webbrowser
import platform
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np

# Import the classifier
try:
    from src.classifier import SimpleQwen3Classifier
except ImportError:
    # Handle case where script is run from different directory
    sys.path.append(str(Path(__file__).parent))
    from src.classifier import SimpleQwen3Classifier

# --- Configuration ---
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Microsoft Graph Graph Explorer ID (public)
TENANT_ID = "common"
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

# --- Templates (from generate_personal_devui_package.py) ---
MEETING_TYPE_TEMPLATES = {
    "Quarterly Business Review (QBR)": {
        "category": "Strategic Planning",
        "complexity": "high",
        "leadTime": 45,
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_get_manager"],
        "promptTemplate": """I have an upcoming Quarterly Business Review titled "{subject}" scheduled for {datetime} with {attendees} attendees.

Please find and access this specific event on my calendar (search for: "{subject}" on {date} at {time}) to get the complete details including:
- Full attendee list with names and emails
- Meeting location: {location}
- Meeting description and agenda
- Any attached documents or related materials

Then create a detailed workback plan that includes:
1. All key milestones leading up to the meeting
2. Specific tasks with owners assigned from the actual attendee list
3. Dependencies between tasks
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Use the actual attendee names from this calendar event for task assignments
- Reference the meeting location for any venue/setup tasks
- Check for related emails, documents, or previous meeting notes
- Coordinate across teams based on attendee organizational roles

Generate a comprehensive workback plan that ensures successful meeting preparation."""
    },
    "Product Launch": {
        "category": "Product Management",
        "complexity": "high",
        "leadTime": 90,
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_get_document"],
        "promptTemplate": """I have an upcoming product launch event titled "{subject}" scheduled for {datetime} with {attendees} attendees.

Please find and access this specific event on my calendar (search for: "{subject}" on {date} at {time}) to retrieve:
- Complete attendee list with names, emails, and roles
- Meeting location: {location}
- Event description and launch details
- Any linked documents, presentations, or launch materials

Then create a detailed workback plan that includes:
1. All key milestones leading up to the launch
2. Specific tasks with owners from the actual attendee list
3. Dependencies between tasks
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Identify product, marketing, and support team members from the attendee list
- Use actual attendee names for task ownership and responsibilities
- Reference the launch scope and timeline from the meeting description
- Check for related product roadmap documents or specifications
- Coordinate cross-functional teams based on attendee roles

Generate a comprehensive workback plan that ensures successful product launch."""
    },
    "Conference/Event Preparation": {
        "category": "Events & Communications",
        "complexity": "medium",
        "leadTime": 45,
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_send_mail"],
        "promptTemplate": """I have an upcoming conference event titled "{subject}" scheduled for {datetime} with {attendees} attendees.

Please find and access this specific calendar event (search for: "{subject}" on {date} at {time}) to retrieve:
- Full attendee list identifying speakers, organizers, VIPs, and participants
- Event venue and location details: {location}
- Conference description, themes, and session topics
- Any planning documents or speaker materials

Then create a detailed workback plan that includes:
1. All key milestones leading up to the conference
2. Specific tasks with owners from the attendee/organizer list
3. Dependencies between tasks
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Identify speakers, session chairs, and organizing committee from attendee list
- Use the venue location for logistics planning (AV, catering, setup)
- Reference conference themes from the meeting description
- Assign speaker coordination tasks to actual organizer names
- Plan venue setup based on the actual location details

Generate a comprehensive workback plan that ensures successful conference execution."""
    },
    "Executive Presentation": {
        "category": "Leadership Communications",
        "complexity": "medium",
        "leadTime": 21,
        "expectedTools": ["graph_calendar_get_events", "graph_get_document", "bizchat_search"],
        "promptTemplate": """I have an upcoming executive presentation titled "{subject}" scheduled for {datetime}.

Please find and access this specific calendar event (search for: "{subject}" on {date} at {time}) to retrieve:
- Complete list of executive attendees with names and titles
- Presentation venue: {location}
- Meeting description and presentation topics
- Any pre-shared materials or agenda documents

Then create a detailed workback plan that includes:
1. All key milestones leading up to the presentation
2. Specific tasks with owners identified from the attendee list
3. Dependencies between tasks (data collection, slide creation, reviews)
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Identify the executive audience from the attendee list (VPs, SVPs, C-level)
- Assign slide creation and review tasks to actual people on the invite
- Reference the presentation topics from the meeting description
- Check for related strategic documents or previous presentations
- Plan rehearsals with the actual presenters from the attendee list

Generate a comprehensive workback plan that ensures a successful executive presentation."""
    },
    "Budget Planning": {
        "category": "Financial Planning",
        "complexity": "medium",
        "leadTime": 30,
        "expectedTools": ["graph_calendar_get_events", "graph_get_document"],
        "promptTemplate": """I have an upcoming budget planning meeting titled "{subject}" scheduled for {datetime} with {attendees} stakeholders.

Please find and access this specific calendar event (search for: "{subject}" on {date} at {time}) to retrieve:
- Complete attendee list with budget owners, finance team, and approvers
- Meeting location: {location}
- Budget planning scope and fiscal period from meeting description
- Any linked budget templates or financial documents

Then create a detailed workback plan that includes:
1. All key milestones leading up to the budget approval
2. Specific tasks with owners identified from the attendee list
3. Dependencies between tasks (data collection, analysis, reviews, approvals)
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Review the attendee list to identify budget owners, finance team members, and approvers
- Budget data needs to be collected from multiple departments
- Financial analysis and variance reporting are required
- Multiple review and approval cycles with finance and leadership
- Budget justifications and business cases need to be prepared
- Historical data analysis and forecasting are needed

Generate a comprehensive workback plan that ensures successful budget planning and approval."""
    },
    "Project Kickoff": {
        "category": "Project Management",
        "complexity": "medium",
        "leadTime": 14,
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "ado_get_work_items"],
        "promptTemplate": """I have an upcoming project kickoff meeting titled "{subject}" scheduled for {datetime} with {attendees} team members.

Please find and access this specific calendar event (search for: "{subject}" on {date} at {time}) to retrieve:
- Complete attendee list with project team members and stakeholders
- Meeting location: {location}
- Project scope, goals, and deliverables from the meeting description
- Any attached project charters or planning documents

Then create a detailed workback plan that includes:
1. All key milestones for the project execution
2. Specific tasks with owners assigned from the actual attendee list
3. Dependencies between tasks
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Identify the project manager, core team, and stakeholders from the attendee list
- Use actual attendee names for task assignments
- Reference the project goals from the meeting description
- Check for related project documentation or specifications
- Coordinate cross-functional dependencies based on attendee roles

Generate a comprehensive workback plan that ensures a successful project kickoff and execution."""
    },
    "Hiring Committee": {
        "category": "Talent Acquisition",
        "complexity": "low",
        "leadTime": 7,
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_send_mail"],
        "promptTemplate": """I have an upcoming hiring committee meeting titled "{subject}" scheduled for {datetime} with {attendees} interviewers.

Please find and access this specific calendar event (search for: "{subject}" on {date} at {time}) to retrieve:
- Complete list of interviewers and hiring managers
- Meeting location: {location}
- Candidate details and role information from the meeting description
- Any attached resumes or interview feedback forms

Then create a detailed workback plan that includes:
1. All key milestones for the hiring decision process
2. Specific tasks with owners assigned from the attendee list (feedback collection, debrief)
3. Dependencies between tasks
4. Critical path activities (offer generation, background checks)
5. Risk mitigation strategies

Please consider:
- Identify the hiring manager and interview panel from the attendee list
- Assign feedback submission tasks to actual interviewers
- Reference the candidate and role details from the meeting description
- Check for related interview feedback or candidate documents
- Coordinate with HR and the hiring manager based on attendee roles

Generate a comprehensive workback plan that ensures a smooth hiring decision process."""
    },
    "Training Workshop": {
        "category": "Learning & Development",
        "complexity": "medium",
        "leadTime": 60,
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_send_mail"],
        "promptTemplate": """I have an upcoming training workshop titled "{subject}" scheduled for {datetime} with {attendees} participants.

Please find and access this specific calendar event (search for: "{subject}" on {date} at {time}) to retrieve:
- Complete list of participants and trainers
- Workshop venue: {location}
- Training agenda and learning objectives from the meeting description
- Any attached training materials or pre-read documents

Then create a detailed workback plan that includes:
1. All key milestones for the workshop preparation and delivery
2. Specific tasks with owners assigned from the organizer/trainer list
3. Dependencies between tasks (content creation, logistics, registration)
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Identify the trainers and logistics coordinators from the attendee list
- Use the venue location for setup and catering planning
- Reference the learning objectives from the meeting description
- Assign content preparation tasks to actual trainers
- Plan participant communication and registration tracking

Generate a comprehensive workback plan that ensures a successful training workshop."""
    }
}

SYNTHETIC_SCENARIOS = [
    {
        "title": "Board of Directors Quarterly Strategy Review",
        "category": "Strategic Planning",
        "complexity": "high",
        "leadTime": 60,
        "description": "Present Q4 performance, annual strategy, and FY26 roadmap to the Board of Directors",
        "attendees": 15,
        "userRole": "organizer",
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_get_document", "bizchat_search"],
        "scenario": "You are presenting to the Board of Directors covering quarterly results, strategic initiatives, competitive landscape, and next year's investment priorities. This is a high-stakes presentation requiring extensive preparation, data analysis, and stakeholder alignment."
    },
    {
        "title": "Major Customer Executive Business Review (Fortune 100)",
        "category": "Strategic Planning",
        "complexity": "high",
        "leadTime": 45,
        "description": "Executive business review with a Fortune 100 customer covering partnership value, roadmap, and expansion opportunities",
        "attendees": 20,
        "userRole": "organizer",
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_get_document", "bizchat_search"],
        "scenario": "Conduct a strategic business review with your largest enterprise customer's C-suite. Need to demonstrate value delivered, address concerns, showcase future capabilities, and identify expansion opportunities worth millions in annual recurring revenue."
    },
    {
        "title": "Annual Product Strategy Offsite with CVP",
        "category": "Product Management",
        "complexity": "high",
        "leadTime": 90,
        "description": "3-day offsite to define product vision, strategy, and OKRs for the next fiscal year",
        "attendees": 30,
        "userRole": "organizer",
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_get_document", "ado_get_work_items"],
        "scenario": "Lead a 3-day offsite with product leadership and engineering directors to define the annual product strategy, prioritize investments across multiple product lines, set ambitious OKRs, and align on execution plans with CVP approval."
    },
    {
        "title": "Crisis Management: Major Service Outage Communication",
        "category": "Leadership Communications",
        "complexity": "high",
        "leadTime": 7,
        "description": "Coordinate crisis response and executive communications for a major service outage affecting millions of users",
        "attendees": 25,
        "userRole": "organizer",
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_send_mail", "bizchat_search"],
        "scenario": "A critical service outage has impacted millions of customers. You need to coordinate incident response, prepare executive communications, manage customer notifications, and organize war room logistics. Time is critical and stakes are high."
    },
    {
        "title": "Company-Wide Product Training Launch (M365 Pulse)",
        "category": "Learning & Development",
        "complexity": "high",
        "leadTime": 45,
        "description": "Launch enterprise-wide training program on new M365 Pulse features for 374+ participants across global offices",
        "attendees": 374,
        "userRole": "participant",
        "expectedTools": ["graph_calendar_get_events", "graph_get_people", "graph_send_mail", "graph_get_document"],
        "scenario": "Participate in planning the launch of a comprehensive training program introducing M365 Pulse to the entire organization. With 374 participants across multiple time zones, this requires coordinating trainers, preparing materials, setting up virtual infrastructure, creating feedback loops, and ensuring maximum adoption of critical productivity tools."
    }
]

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class MimicTool:
    def __init__(self, user_email: str, model_path: str = "models/qwen3-embedding"):
        self.user_email = user_email
        self.model_path = model_path
        self.access_token = None
        self.classifier = None
        
    def authenticate(self):
        """Authenticate user based on platform"""
        system = platform.system()
        
        if system == "Windows":
            return self.authenticate_windows()
        else:
            return self.authenticate_device_flow()

    def authenticate_windows(self):
        """Authenticate using MSAL on Windows (supports SSO/Broker)"""
        print("\n🔐 Authenticating via Windows (MSAL)...")
        try:
            import msal
        except ImportError:
            print("⚠️ MSAL not installed. Falling back to Device Code Flow.")
            return self.authenticate_device_flow()

        # Cache setup
        cache = msal.SerializableTokenCache()
        cache_file = Path("token_cache.bin")
        if cache_file.exists():
            try:
                cache.deserialize(open(cache_file, "r").read())
            except:
                pass

        # Setup App
        app = msal.PublicClientApplication(
            CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            token_cache=cache
        )
        
        scopes = ["https://graph.microsoft.com/.default", "offline_access"]
        result = None
        
        # 1. Try Silent (Cached)
        accounts = app.get_accounts()
        if accounts:
            print(f"   Found account: {accounts[0]['username']}")
            result = app.acquire_token_silent(scopes, account=accounts[0])
            
        # 2. Try Interactive
        if not result:
            print("   No silent token found. Launching interactive login...")
            try:
                result = app.acquire_token_interactive(scopes=scopes)
            except Exception as e:
                print(f"❌ Interactive auth failed: {e}")
                
        if result and "access_token" in result:
            self.access_token = result["access_token"]
            print("✅ Authentication successful!")
            # Save cache
            if cache.has_state_changed:
                with open(cache_file, "w") as f:
                    f.write(cache.serialize())
            return True
        else:
            print("⚠️ Windows auth failed or cancelled. Falling back to Device Code Flow.")
            return self.authenticate_device_flow()

    def authenticate_device_flow(self):
        """Authenticate using Device Code Flow"""
        print("\n🔐 Authenticating with Microsoft Graph (Device Flow)...")
        
        # 1. Get Device Code
        url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
        data = {
            "client_id": CLIENT_ID,
            "scope": "https://graph.microsoft.com/.default offline_access"
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            device_auth = response.json()
        except Exception as e:
            print(f"❌ Failed to initiate authentication: {e}")
            return False
            
        print(f"\n📱 Please visit: {device_auth['verification_uri']}")
        print(f"🔑 Enter code: {device_auth['user_code']}")
        
        # Try to open browser
        try:
            webbrowser.open(device_auth['verification_uri'])
        except:
            pass
            
        print("\n⏳ Waiting for you to sign in...")
        
        # 2. Poll for Token
        interval = device_auth.get('interval', 5)
        expires_in = device_auth.get('expires_in', 900)
        start_time = time.time()
        
        token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        token_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": CLIENT_ID,
            "device_code": device_auth['device_code']
        }
        
        while time.time() - start_time < expires_in:
            time.sleep(interval)
            try:
                resp = requests.post(token_url, data=token_data)
                token_resp = resp.json()
                
                if 'access_token' in token_resp:
                    self.access_token = token_resp['access_token']
                    print("✅ Authentication successful!")
                    return True
                elif token_resp.get('error') == 'authorization_pending':
                    continue
                else:
                    print(f"❌ Auth error: {token_resp.get('error_description')}")
                    return False
            except Exception as e:
                print(f"❌ Polling error: {e}")
                return False
                
        print("❌ Authentication timed out.")
        return False

    def fetch_meetings(self, days: int = 180) -> List[Dict]:
        """Fetch calendar events for the last N days"""
        if not self.access_token:
            print("❌ Not authenticated.")
            return []
            
        print(f"\n📅 Fetching calendar data for last {days} days...")
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Prefer": 'outlook.timezone="UTC"'
        }
        
        events = []
        url = f"{GRAPH_ENDPOINT}/me/calendar/events"
        params = {
            "$filter": f"start/dateTime ge '{start_date.isoformat()}' and end/dateTime le '{end_date.isoformat()}'",
            "$select": "subject,bodyPreview,start,end,attendees,organizer,location",
            "$top": 100
        }
        
        while url:
            try:
                resp = requests.get(url, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()
                
                batch = data.get('value', [])
                events.extend(batch)
                print(f"   Fetched {len(events)} events...", end='\r')
                
                url = data.get('@odata.nextLink')
                params = None # params only needed for first request
            except Exception as e:
                print(f"\n❌ Error fetching events: {e}")
                break
                
        print(f"\n✅ Total events fetched: {len(events)}")
        return events

    def load_classifier(self):
        """Load the Qwen3-Embedding classifier"""
        print("\n🚀 Loading AI Model (Qwen3-Embedding)...")
        try:
            self.classifier = SimpleQwen3Classifier(self.model_path)
            print("✅ Model loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            sys.exit(1)

    def process_meetings(self, meetings: List[Dict]) -> List[Dict]:
        """Classify and estimate value for all meetings"""
        if not self.classifier:
            self.load_classifier()
            
        print("\n🤖 Analyzing meetings...")
        results = []
        
        total = len(meetings)
        for i, meeting in enumerate(meetings):
            subject = meeting.get('subject', 'Untitled')
            body = meeting.get('bodyPreview', '')
            attendees = meeting.get('attendees', [])
            attendee_count = len(attendees)
            
            # Skip very small meetings (optional, but good for noise reduction)
            if attendee_count < 2:
                continue
                
            # 1. Estimate Value
            score, reasoning = self.classifier.estimate_value(subject, body, attendee_count)
            
            # 2. Classify Category
            category, conf = self.classifier.classify_meeting(subject, body, attendee_count)
            
            # Determine role
            organizer = meeting.get('organizer', {}).get('emailAddress', {}).get('address', '').lower()
            role = "organizer" if organizer == self.user_email.lower() else "participant"
            
            results.append({
                "meeting": meeting,
                "score": score,
                "category": category,
                "reasoning": reasoning,
                "role": role
            })
            
            if i % 10 == 0:
                print(f"   Processed {i}/{total}...", end='\r')
                
        print(f"\n✅ Analyzed {len(results)} relevant meetings.")
        return results

    def _create_prompt_from_meeting(self, meeting: Dict, template: Dict) -> str:
        """Create a grounded prompt from a real meeting using the rich template"""
        subject = meeting.get('subject', 'Untitled')
        start_dt = meeting.get('start', {}).get('dateTime', '')
        attendee_count = len(meeting.get('attendees', []))
        location = meeting.get('location', {}).get('displayName', '')
        
        # Format date and time for unique identification
        try:
            # Handle various date formats (ISO with/without Z, etc)
            clean_dt = start_dt.replace('Z', '+00:00').split('.')[0]
            dt = datetime.fromisoformat(clean_dt)
            date_str = dt.strftime("%B %d, %Y")
            time_str = dt.strftime("%I:%M %p")
            datetime_str = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            date_str = "the scheduled date"
            time_str = ""
            datetime_str = "the scheduled date and time"
        
        # Use the template if available, otherwise fallback to a generic rich prompt
        if 'promptTemplate' in template:
            prompt_text = template['promptTemplate'].format(
                subject=subject,
                date=date_str,
                datetime=datetime_str,
                time=time_str,
                attendees=attendee_count,
                location=location if location else "the scheduled location"
            )
        else:
            # Generic fallback for categories without specific templates
            prompt_text = f"""I have an upcoming meeting titled "{subject}" scheduled for {datetime_str} with {attendee_count} attendees.

Please find and access this specific event on my calendar (search for: "{subject}" on {date_str} at {time_str}) to get the complete details including:
- Full attendee list with names and emails
- Meeting location: {location if location else "the scheduled location"}
- Meeting description and agenda
- Any attached documents or related materials

Then create a detailed workback plan that includes:
1. All key milestones leading up to the meeting
2. Specific tasks with owners assigned from the actual attendee list
3. Dependencies between tasks
4. Critical path activities
5. Risk mitigation strategies

Please consider:
- Use the actual attendee names from this calendar event for task assignments
- Reference the meeting location for any venue/setup tasks
- Check for related emails, documents, or previous meeting notes
- Coordinate across teams based on attendee organizational roles

Generate a comprehensive workback plan that ensures successful meeting preparation."""

        return prompt_text

    def generate_html_package(self, analyzed_meetings: List[Dict]):
        """Generate the HTML interface with 5 Synthetic + 5 Real + 15 Candidates"""
        print("\n📦 Generating Mimic Interface...")
        
        # 1. Sort by score (descending)
        analyzed_meetings.sort(key=lambda x: x['score'], reverse=True)
        
        # 2. Select Top 5 Real High-Value (Must have rich metadata)
        top_5_real = []
        candidates = []
        
        # Filter for rich metadata (must have attendees and body/subject)
        rich_meetings = [
            m for m in analyzed_meetings 
            if len(m['meeting'].get('attendees', [])) >= 2 
            and m['meeting'].get('subject')
        ]
        
        if len(rich_meetings) < 5:
            print(f"⚠️ Warning: Only found {len(rich_meetings)} meetings with rich metadata (need 5).")
            
        top_5_real = rich_meetings[:5]
        candidates = rich_meetings[5:20] # Next 15
        
        # 4. Prepare Prompt Data
        prompts_data = []
        prompt_id = 1
        
        # A. Add 5 Synthetic Scenarios
        for scenario in SYNTHETIC_SCENARIOS:
            # Build role-specific context
            role = scenario['userRole']
            if role == 'organizer':
                role_context = "As the organizer and leader of this high-stakes meeting, you are responsible for its success and strategic outcomes."
                role_tasks = """- Define meeting objectives and desired outcomes
- Identify and invite key stakeholders and decision makers
- Prepare comprehensive presentation materials and data analysis
- Coordinate pre-reads and background materials
- Plan for contingencies and difficult questions
- Arrange logistics (venue, technology, catering for multi-day events)
- Schedule preparation sessions with your team
- Create detailed agenda with time allocations"""
            else:
                role_context = "As a key participant in this strategic meeting, you need to be thoroughly prepared to contribute effectively."
                role_tasks = """- Review all meeting materials and background documents
- Prepare your perspective and recommendations
- Identify questions and concerns to raise
- Coordinate with your team on unified position
- Research relevant data and competitive intelligence
- Prepare to take detailed notes and action items
- Plan follow-up actions and next steps"""
            
            prompt_text = f"""**[EXPLORATION SCENARIO - Not from your calendar]**

This is a hypothetical high-value scenario designed to explore how BizChat can help with complex meeting preparation.

Scenario: {scenario['title']}
Timeframe: This meeting is scheduled {scenario['leadTime']} days from now.

{scenario['scenario']}

{role_context}

Meeting Details:
- Category: {scenario['category']}
- Complexity: {scenario['complexity'].upper()}
- Lead Time Available: {scenario['leadTime']} days until the meeting
- Expected Attendees: ~{scenario['attendees']} people

Please use your imagination to create a comprehensive workback plan for this scenario:

{role_tasks}

**Goal**: Experience how BizChat assists with high-stakes, complex meeting preparation. Save the DevUI session link to help us collect data for improving high-value scenarios."""

            prompts_data.append({
                "id": prompt_id,
                "title": scenario['title'],
                "category": scenario['category'],
                "complexity": scenario['complexity'],
                "leadTime": scenario['leadTime'],
                "description": scenario['description'],
                "attendees": scenario['attendees'],
                "userRole": scenario['userRole'],
                "valueScore": 95.0, # Synthetic are always high value
                "reasoning": "Synthetic High-Value Scenario",
                "autoSelected": True,
                "isSynthetic": True,
                "prompt": prompt_text,
                "expectedTools": scenario['expectedTools'],
                "status": "not-started",
                "selected": False,
                # Rich Metadata for Synthetic
                "meetingDate": f"Future Date (+{scenario['leadTime']} days)",
                "location": "TBD (Virtual/Hybrid)",
                "organizer": "You (Organizer)" if scenario['userRole'] == 'organizer' else "TBD"
            })
            prompt_id += 1
            
        # B. Add Top 5 Real Meetings
        for item in top_5_real:
            meeting = item['meeting']
            category = item['category']
            # Get template or fallback
            template = MEETING_TYPE_TEMPLATES.get(category, MEETING_TYPE_TEMPLATES["Quarterly Business Review (QBR)"])
            
            # Generate RICH prompt
            prompt_text = self._create_prompt_from_meeting(meeting, template)
            
            # Extract Rich Metadata
            start_time = meeting.get('start', {}).get('dateTime', '')
            try:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                formatted_date = start_time
                
            location = meeting.get('location', {}).get('displayName', 'Teams Meeting')
            organizer_name = meeting.get('organizer', {}).get('emailAddress', {}).get('name', 'Unknown')
            organizer_email = meeting.get('organizer', {}).get('emailAddress', {}).get('address', '')
            organizer_str = f"{organizer_name} ({organizer_email})" if organizer_email else organizer_name

            prompts_data.append({
                "id": prompt_id,
                "title": meeting.get('subject'),
                "category": category,
                "complexity": template.get('complexity', 'medium'),
                "leadTime": template.get('leadTime', 14),
                "description": meeting.get('bodyPreview', '')[:200] + "...",
                "attendees": len(meeting.get('attendees', [])),
                "userRole": item['role'],
                "valueScore": item['score'],
                "reasoning": item['reasoning'],
                "autoSelected": True,
                "isSynthetic": False,
                "prompt": prompt_text,
                "expectedTools": template['expectedTools'],
                "status": "not-started",
                "selected": False,
                # Rich Metadata
                "meetingDate": formatted_date,
                "location": location,
                "organizer": organizer_str
            })
            prompt_id += 1
            
        # C. Add 15 Candidates
        for item in candidates:
            meeting = item['meeting']
            category = item['category']
            template = MEETING_TYPE_TEMPLATES.get(category, MEETING_TYPE_TEMPLATES["Quarterly Business Review (QBR)"])
            
            # Generate RICH prompt
            prompt_text = self._create_prompt_from_meeting(meeting, template)
            
            # Extract Rich Metadata
            start_time = meeting.get('start', {}).get('dateTime', '')
            try:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                formatted_date = start_time
                
            location = meeting.get('location', {}).get('displayName', 'Teams Meeting')
            organizer_name = meeting.get('organizer', {}).get('emailAddress', {}).get('name', 'Unknown')
            organizer_email = meeting.get('organizer', {}).get('emailAddress', {}).get('address', '')
            organizer_str = f"{organizer_name} ({organizer_email})" if organizer_email else organizer_name
            
            prompts_data.append({
                "id": prompt_id,
                "title": meeting.get('subject'),
                "category": category,
                "complexity": template.get('complexity', 'medium'),
                "leadTime": template.get('leadTime', 14),
                "description": meeting.get('bodyPreview', '')[:200] + "...",
                "attendees": len(meeting.get('attendees', [])),
                "userRole": item['role'],
                "valueScore": item['score'],
                "reasoning": item['reasoning'],
                "autoSelected": False, # Not auto-selected
                "isSynthetic": False,
                "prompt": prompt_text,
                "expectedTools": template['expectedTools'],
                "status": "not-started",
                "selected": False,
                # Rich Metadata
                "meetingDate": formatted_date,
                "location": location,
                "organizer": organizer_str
            })
            prompt_id += 1
            
        # 5. Inject into HTML Template
        template_path = Path("templates/devui_prompts_manager.html")
        if not template_path.exists():
            print("❌ Template file not found!")
            return
            
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Replace Data
        json_data = json.dumps(prompts_data, indent=4, cls=NumpyEncoder)
        
        start_marker = "const PROMPTS_DATA = ["
        end_marker = "        ];"
        
        start_idx = html_content.find(start_marker)
        end_idx = html_content.find(end_marker, start_idx) + len(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            new_section = f"const PROMPTS_DATA = {json_data};"
            html_content = html_content[:start_idx] + new_section + html_content[end_idx:]
            
        # Update Header
        html_content = html_content.replace(
            "<p>TimeBerry T+P | November 18, 2025</p>",
            f"<p>Mimic Generated for: {self.user_email} | {datetime.now().strftime('%B %d, %Y')}</p>"
        )
        
        # Save
        output_filename = f"mimic_{self.user_email.split('@')[0]}.html"
        output_path = Path("output") / output_filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"\n✅ Mimic Interface generated: {output_path}")
        print(f"   Open this file in your browser to start annotation.")
        
        # Try to open
        try:
            webbrowser.open(f"file://{output_path.absolute()}")
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="Mimic: Meeting Value Estimator & Workback Plan Generator")
    parser.add_argument("email", help="User email address (used for identity and role detection)")
    parser.add_argument("--file", help="Optional: Use local JSON file instead of Graph API")
    parser.add_argument("--days", type=int, default=180, help="Number of days to look back (default: 180)")
    
    args = parser.parse_args()
    
    tool = MimicTool(args.email)
    
    meetings = []
    if args.file:
        print(f"📂 Loading local file: {args.file}")
        with open(args.file, 'r') as f:
            data = json.load(f)
            all_meetings = data.get('events', data) if isinstance(data, dict) else data
            
            # Filter by date if using local file to mimic API behavior
            print(f"📅 Filtering for last {args.days} days...")
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=args.days)
            
            meetings = []
            for m in all_meetings:
                # Handle various date formats
                start_str = m.get('start', {}).get('dateTime') or m.get('start')
                if start_str:
                    try:
                        # Simple ISO parsing (handles 'Z' and offsets roughly)
                        evt_date = datetime.fromisoformat(start_str.replace('Z', '+00:00').split('.')[0])
                        if start_date <= evt_date <= end_date:
                            meetings.append(m)
                    except:
                        pass # Skip if date parse fails
            print(f"✅ Found {len(meetings)} meetings in range.")
            
    else:
        if tool.authenticate():
            meetings = tool.fetch_meetings(days=args.days)
        else:
            print("❌ Authentication failed. Exiting.")
            sys.exit(1)
            
    if not meetings:
        print("❌ No meetings found.")
        sys.exit(1)
        
    analyzed = tool.process_meetings(meetings)
    tool.generate_html_package(analyzed)

if __name__ == "__main__":
    main()
