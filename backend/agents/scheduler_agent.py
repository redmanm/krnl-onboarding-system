import json
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta, date
from database import get_db
from models import CalendarEvent, Employee
from .base_agent import BaseAgent
import uuid

class MockGoogleCalendarAPI:
    """Mock Google Calendar API for demonstration purposes"""
    
    def __init__(self):
        self.events = {}
        self.event_counter = 1
    
    def create_event(self, summary: str, description: str, 
                    start_time: datetime, end_time: datetime, 
                    attendees: List[str] = None) -> Dict[str, Any]:
        """Create a mock calendar event"""
        event_id = f"mock_event_{self.event_counter}"
        self.event_counter += 1
        
        event = {
            "id": event_id,
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC"
            },
            "attendees": [{"email": email} for email in (attendees or [])],
            "status": "confirmed",
            "created": datetime.utcnow().isoformat(),
            "updated": datetime.utcnow().isoformat()
        }
        
        self.events[event_id] = event
        return event
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get a mock calendar event"""
        return self.events.get(event_id)
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a mock calendar event"""
        if event_id in self.events:
            self.events[event_id].update(updates)
            self.events[event_id]["updated"] = datetime.utcnow().isoformat()
        return self.events.get(event_id)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a mock calendar event"""
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False

class SchedulerAgent(BaseAgent):
    """Agent responsible for scheduling calendar events"""
    
    def __init__(self):
        super().__init__("scheduler")
        self.calendar_api = MockGoogleCalendarAPI()
        self.onboarding_templates = {
            "orientation": {
                "duration_hours": 4,
                "title": "New Employee Orientation - {name}",
                "description": """Welcome to KRNL! This orientation session will cover:
                
• Company overview and culture
• Team introductions
• Systems and tools training
• Benefits and policies review
• Q&A session

Please bring a valid ID and complete any pre-boarding forms.
                
Looking forward to welcoming you to the team!"""
            },
            "hr_meeting": {
                "duration_hours": 1,
                "title": "HR Onboarding Meeting - {name}",
                "description": """HR onboarding session covering:
                
• Employment documentation
• Benefits enrollment
• Company policies
• Emergency contacts
• IT equipment setup

Contact HR if you have any questions before the meeting."""
            },
            "team_meet_greet": {
                "duration_hours": 1,
                "title": "Team Meet & Greet - {name}",
                "description": """Informal team meeting to:
                
• Meet your new teammates
• Learn about current projects
• Understand team dynamics
• Set initial goals and expectations

Your manager will introduce you to the team."""
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule onboarding calendar events"""
        employee_data = input_data.get("employee_data", {})
        employee_id = input_data.get("employee_id")
        
        if not employee_id:
            raise ValueError("employee_id is required")
        
        name = employee_data.get("name", "New Employee")
        email = employee_data.get("email", "")
        start_date_str = employee_data.get("start_date", "")
        role = employee_data.get("role", "")
        department = employee_data.get("department", "")
        
        # Parse start date
        if isinstance(start_date_str, str):
            start_date = datetime.fromisoformat(start_date_str).date()
        else:
            start_date = start_date_str
        
        # Schedule multiple onboarding events
        scheduled_events = []
        
        # 1. Orientation (Day 1, Morning)
        orientation_event = await self._schedule_orientation(
            employee_id, name, email, start_date, role, department
        )
        scheduled_events.append(orientation_event)
        
        # 2. HR Meeting (Day 1, Afternoon)
        hr_event = await self._schedule_hr_meeting(
            employee_id, name, email, start_date
        )
        scheduled_events.append(hr_event)
        
        # 3. Team Meet & Greet (Day 2, Morning)
        team_event = await self._schedule_team_meeting(
            employee_id, name, email, start_date + timedelta(days=1), department
        )
        scheduled_events.append(team_event)
        
        result = {
            "events_scheduled": len(scheduled_events),
            "events": scheduled_events,
            "calendar_summary": {
                "employee_name": name,
                "employee_email": email,
                "start_date": start_date.isoformat(),
                "total_events": len(scheduled_events),
                "orientation_scheduled": True,
                "hr_meeting_scheduled": True,
                "team_meeting_scheduled": True
            },
            "next_steps": [
                "Calendar invites will be sent to employee",
                "Manager will be notified of schedule",
                "HR will prepare onboarding materials"
            ]
        }
        
        return result
    
    async def _schedule_orientation(self, employee_id: uuid.UUID, name: str, 
                                  email: str, start_date: date, role: str, 
                                  department: str) -> Dict[str, Any]:
        """Schedule the main orientation event"""
        template = self.onboarding_templates["orientation"]
        
        # Schedule for 9:00 AM on start date
        start_time = datetime.combine(start_date, datetime.min.time().replace(hour=9))
        end_time = start_time + timedelta(hours=template["duration_hours"])
        
        title = template["title"].format(name=name)
        description = template["description"]
        
        # Create calendar event via mock API
        calendar_event = self.calendar_api.create_event(
            summary=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=[email, "hr@krnl.com", "manager@krnl.com"]
        )
        
        # Store in database
        db_event = await self._store_calendar_event(
            employee_id, calendar_event["id"], title, description,
            start_time, end_time, "orientation"
        )
        
        return {
            "type": "orientation",
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "calendar_event_id": calendar_event["id"],
            "db_event_id": str(db_event["id"]),
            "attendees": ["hr@krnl.com", "manager@krnl.com"],
            "status": "scheduled"
        }
    
    async def _schedule_hr_meeting(self, employee_id: uuid.UUID, name: str,
                                 email: str, start_date: date) -> Dict[str, Any]:
        """Schedule HR onboarding meeting"""
        template = self.onboarding_templates["hr_meeting"]
        
        # Schedule for 2:00 PM on start date
        start_time = datetime.combine(start_date, datetime.min.time().replace(hour=14))
        end_time = start_time + timedelta(hours=template["duration_hours"])
        
        title = template["title"].format(name=name)
        description = template["description"]
        
        calendar_event = self.calendar_api.create_event(
            summary=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=[email, "hr@krnl.com"]
        )
        
        db_event = await self._store_calendar_event(
            employee_id, calendar_event["id"], title, description,
            start_time, end_time, "hr_meeting"
        )
        
        return {
            "type": "hr_meeting",
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "calendar_event_id": calendar_event["id"],
            "db_event_id": str(db_event["id"]),
            "attendees": ["hr@krnl.com"],
            "status": "scheduled"
        }
    
    async def _schedule_team_meeting(self, employee_id: uuid.UUID, name: str,
                                   email: str, meeting_date: date, 
                                   department: str) -> Dict[str, Any]:
        """Schedule team meet and greet"""
        template = self.onboarding_templates["team_meet_greet"]
        
        # Schedule for 10:00 AM on second day
        start_time = datetime.combine(meeting_date, datetime.min.time().replace(hour=10))
        end_time = start_time + timedelta(hours=template["duration_hours"])
        
        title = template["title"].format(name=name)
        description = template["description"]
        
        # Add department-specific attendees
        team_emails = self._get_team_emails(department)
        attendees = [email] + team_emails
        
        calendar_event = self.calendar_api.create_event(
            summary=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees
        )
        
        db_event = await self._store_calendar_event(
            employee_id, calendar_event["id"], title, description,
            start_time, end_time, "team_meeting"
        )
        
        return {
            "type": "team_meeting",
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "calendar_event_id": calendar_event["id"],
            "db_event_id": str(db_event["id"]),
            "attendees": team_emails,
            "status": "scheduled"
        }
    
    def _get_team_emails(self, department: str) -> List[str]:
        """Get team email addresses for a department (mock data)"""
        team_mapping = {
            "Engineering": ["tech-lead@krnl.com", "senior-dev@krnl.com"],
            "Product": ["product-manager@krnl.com", "product-owner@krnl.com"],
            "Design": ["design-lead@krnl.com", "ux-designer@krnl.com"],
            "QA": ["qa-lead@krnl.com", "qa-engineer@krnl.com"],
            "DevOps": ["devops-lead@krnl.com", "sre@krnl.com"],
            "Data Science": ["data-lead@krnl.com", "data-scientist@krnl.com"],
            "Marketing": ["marketing-manager@krnl.com", "content-lead@krnl.com"],
            "Sales": ["sales-manager@krnl.com", "sales-rep@krnl.com"],
            "HR": ["hr-manager@krnl.com", "hr-specialist@krnl.com"],
            "Finance": ["finance-manager@krnl.com", "finance-analyst@krnl.com"]
        }
        
        return team_mapping.get(department, ["manager@krnl.com"])
    
    async def _store_calendar_event(self, employee_id: uuid.UUID, event_id: str,
                                  title: str, description: str, start_time: datetime,
                                  end_time: datetime, event_type: str) -> Dict[str, Any]:
        """Store calendar event in database"""
        try:
            db = next(get_db())
            try:
                event = CalendarEvent(
                    employee_id=employee_id,
                    event_id=event_id,
                    title=title,
                    description=description,
                    start_time=start_time,
                    end_time=end_time,
                    status="scheduled"
                )
                
                db.add(event)
                db.commit()
                db.refresh(event)
                
                self.logger.info("Calendar event stored successfully",
                               event_type=event_type,
                               employee_id=str(employee_id))
                
                return {
                    "id": str(event.id),
                    "employee_id": str(event.employee_id),
                    "event_id": event.event_id,
                    "title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "status": event.status,
                    "created_at": event.created_at.isoformat()
                }
            except Exception as e:
                self.logger.error(f"Failed to store calendar event in database: {e}")
                db.rollback()
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"Failed to create database session for calendar event: {e}")
            # Return a mock response if database fails
            return {
                "id": str(uuid.uuid4()),
                "employee_id": str(employee_id),
                "event_id": event_id,
                "title": title,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "status": "scheduled",
                "created_at": datetime.utcnow().isoformat(),
                "note": "Stored in fallback mode due to database error"
            }