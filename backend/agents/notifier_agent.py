import json
from typing import Dict, Any, List
from datetime import datetime
from database import get_db
from models import Notification, Employee
from .base_agent import BaseAgent
import uuid

class MockEmailService:
    """Mock email service for demonstration"""
    
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: List[str] = None, bcc: List[str] = None) -> Dict[str, Any]:
        """Send a mock email"""
        email_id = f"email_{len(self.sent_emails) + 1}"
        
        email = {
            "id": email_id,
            "to": to,
            "cc": cc or [],
            "bcc": bcc or [],
            "subject": subject,
            "body": body,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "sent"
        }
        
        self.sent_emails.append(email)
        return email

class MockSlackService:
    """Mock Slack service for demonstration"""
    
    def __init__(self):
        self.sent_messages = []
    
    def send_message(self, channel: str, text: str, 
                    attachments: List[Dict] = None) -> Dict[str, Any]:
        """Send a mock Slack message"""
        message_id = f"slack_{len(self.sent_messages) + 1}"
        
        message = {
            "id": message_id,
            "channel": channel,
            "text": text,
            "attachments": attachments or [],
            "timestamp": datetime.utcnow().isoformat(),
            "status": "sent"
        }
        
        self.sent_messages.append(message)
        return message

class NotifierAgent(BaseAgent):
    """Agent responsible for sending notifications via email and Slack"""
    
    def __init__(self):
        super().__init__("notifier")
        self.email_service = MockEmailService()
        self.slack_service = MockSlackService()
        
        self.notification_templates = {
            "hr_confirmation": {
                "subject": "New Employee Onboarding Initiated - {name}",
                "email_body": """Dear HR Team,

A new employee onboarding process has been initiated for:

Employee Details:
• Name: {name}
• Email: {email}
• Role: {role}
• Department: {department}
• Start Date: {start_date}

Onboarding Status:
• Data Validation: ✅ Completed
• System Account: ✅ Created (Username: {username})
• Calendar Events: ✅ Scheduled ({event_count} events)
• Notifications: ✅ In Progress

Next Steps:
1. Review employee documentation
2. Prepare onboarding materials
3. Coordinate with manager for first day
4. Ensure IT equipment is ready

Dashboard: {dashboard_url}

Best regards,
KRNL Onboarding System""",
                "slack_message": "🎉 New employee onboarding initiated for *{name}* ({role}) starting {start_date}. All systems ready! Check dashboard for details."
            },
            
            "manager_notification": {
                "subject": "New Team Member Onboarding - {name}",
                "email_body": """Dear Manager,

Your new team member's onboarding is in progress:

Employee: {name}
Role: {role}
Department: {department}
Start Date: {start_date}

Onboarding Progress:
✅ Employee data validated
✅ System account created (Username: {username})
✅ Calendar events scheduled
✅ HR notifications sent

Scheduled Events:
{scheduled_events}

Please ensure you're prepared for their first day and review the onboarding checklist.

Dashboard: {dashboard_url}

Welcome aboard!
KRNL Onboarding System""",
                "slack_message": "👋 Your new team member *{name}* ({role}) starts {start_date}. Onboarding is complete and ready to go!"
            },
            
            "employee_welcome": {
                "subject": "Welcome to KRNL - Your Onboarding Information",
                "email_body": """Dear {name},

Welcome to KRNL! We're excited to have you join our team.

Your Onboarding Details:
• Start Date: {start_date}
• Role: {role}
• Department: {department}
• System Username: {username}

What's Next:
✅ Your system account has been created
✅ Calendar invites for your first days have been sent
✅ HR and your manager have been notified

First Day Schedule:
{scheduled_events}

Important Information:
• Please arrive at 9:00 AM on your start date
• Bring a valid ID and completed pre-boarding forms
• Your manager will meet you for orientation

If you have any questions before your start date, please don't hesitate to reach out to hr@krnl.com.

We look forward to welcoming you to the team!

Best regards,
The KRNL Team""",
                "slack_message": "🎊 Welcome {name}! Your onboarding is complete. See you on {start_date}!"
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notifications to relevant parties"""
        employee_data = input_data.get("employee_data", {})
        employee_id = input_data.get("employee_id")
        account_data = input_data.get("account_data", {})
        calendar_data = input_data.get("calendar_data", {})
        
        if not employee_id:
            raise ValueError("employee_id is required")
        
        name = employee_data.get("name", "")
        email = employee_data.get("email", "")
        role = employee_data.get("role", "")
        department = employee_data.get("department", "")
        start_date = employee_data.get("start_date", "")
        
        username = account_data.get("username", "")
        events = calendar_data.get("events", [])
        
        sent_notifications = []
        
        # 1. Send HR confirmation
        hr_notification = await self._send_hr_confirmation(
            employee_id, name, email, role, department, start_date, 
            username, len(events)
        )
        sent_notifications.append(hr_notification)
        
        # 2. Send manager notification
        manager_notification = await self._send_manager_notification(
            employee_id, name, email, role, department, start_date, 
            username, events
        )
        sent_notifications.append(manager_notification)
        
        # 3. Send employee welcome (if email provided)
        if email:
            employee_notification = await self._send_employee_welcome(
                employee_id, name, email, role, department, start_date, 
                username, events
            )
            sent_notifications.append(employee_notification)
        
        result = {
            "notifications_sent": len(sent_notifications),
            "notifications": sent_notifications,
            "summary": {
                "hr_notified": True,
                "manager_notified": True,
                "employee_notified": bool(email),
                "total_sent": len(sent_notifications),
                "channels_used": ["email", "slack"]
            },
            "next_steps": [
                "Monitor for read receipts",
                "Follow up if no response within 24 hours",
                "Prepare for employee start date"
            ]
        }
        
        return result
    
    async def _send_hr_confirmation(self, employee_id: uuid.UUID, name: str, 
                                  email: str, role: str, department: str, 
                                  start_date: str, username: str, 
                                  event_count: int) -> Dict[str, Any]:
        """Send HR confirmation notification"""
        template = self.notification_templates["hr_confirmation"]
        
        # Prepare template data
        template_data = {
            "name": name,
            "email": email,
            "role": role,
            "department": department,
            "start_date": start_date,
            "username": username,
            "event_count": event_count,
            "dashboard_url": "http://localhost:3000/dashboard"
        }
        
        # Send email
        email_response = self.email_service.send_email(
            to="hr@krnl.com",
            subject=template["subject"].format(**template_data),
            body=template["email_body"].format(**template_data),
            cc=["manager@krnl.com"]
        )
        
        # Send Slack message
        slack_response = self.slack_service.send_message(
            channel="#hr-notifications",
            text=template["slack_message"].format(**template_data)
        )
        
        # Store in database
        db_notification = await self._store_notification(
            employee_id, "hr_confirmation", "hr@krnl.com",
            template["subject"].format(**template_data),
            template["email_body"].format(**template_data)
        )
        
        return {
            "type": "hr_confirmation",
            "recipient": "hr@krnl.com",
            "channels": ["email", "slack"],
            "email_id": email_response["id"],
            "slack_id": slack_response["id"],
            "db_notification_id": str(db_notification["id"]),
            "status": "sent"
        }
    
    async def _send_manager_notification(self, employee_id: uuid.UUID, name: str,
                                       email: str, role: str, department: str,
                                       start_date: str, username: str,
                                       events: List[Dict]) -> Dict[str, Any]:
        """Send manager notification"""
        template = self.notification_templates["manager_notification"]
        
        # Format scheduled events
        scheduled_events = "\n".join([
            f"• {event.get('title', 'Event')} - {event.get('start_time', 'TBD')}"
            for event in events
        ])
        
        template_data = {
            "name": name,
            "email": email,
            "role": role,
            "department": department,
            "start_date": start_date,
            "username": username,
            "scheduled_events": scheduled_events,
            "dashboard_url": "http://localhost:3000/dashboard"
        }
        
        # Get manager email (in real system, this would be from employee data)
        manager_email = self._get_manager_email(department)
        
        email_response = self.email_service.send_email(
            to=manager_email,
            subject=template["subject"].format(**template_data),
            body=template["email_body"].format(**template_data)
        )
        
        slack_response = self.slack_service.send_message(
            channel=f"#{department.lower()}-team",
            text=template["slack_message"].format(**template_data)
        )
        
        db_notification = await self._store_notification(
            employee_id, "manager_notification", manager_email,
            template["subject"].format(**template_data),
            template["email_body"].format(**template_data)
        )
        
        return {
            "type": "manager_notification",
            "recipient": manager_email,
            "channels": ["email", "slack"],
            "email_id": email_response["id"],
            "slack_id": slack_response["id"],
            "db_notification_id": str(db_notification["id"]),
            "status": "sent"
        }
    
    async def _send_employee_welcome(self, employee_id: uuid.UUID, name: str,
                                   email: str, role: str, department: str,
                                   start_date: str, username: str,
                                   events: List[Dict]) -> Dict[str, Any]:
        """Send welcome message to employee"""
        template = self.notification_templates["employee_welcome"]
        
        # Format scheduled events for employee
        scheduled_events = "\n".join([
            f"• {event.get('title', 'Event')} - {self._format_time(event.get('start_time', ''))}"
            for event in events
        ])
        
        template_data = {
            "name": name,
            "role": role,
            "department": department,
            "start_date": start_date,
            "username": username,
            "scheduled_events": scheduled_events
        }
        
        email_response = self.email_service.send_email(
            to=email,
            subject=template["subject"].format(**template_data),
            body=template["email_body"].format(**template_data),
            bcc=["hr@krnl.com"]
        )
        
        db_notification = await self._store_notification(
            employee_id, "employee_welcome", email,
            template["subject"].format(**template_data),
            template["email_body"].format(**template_data)
        )
        
        return {
            "type": "employee_welcome",
            "recipient": email,
            "channels": ["email"],
            "email_id": email_response["id"],
            "db_notification_id": str(db_notification["id"]),
            "status": "sent"
        }
    
    def _get_manager_email(self, department: str) -> str:
        """Get manager email for department (mock data)"""
        manager_emails = {
            "Engineering": "engineering-manager@krnl.com",
            "Product": "product-manager@krnl.com",
            "Design": "design-manager@krnl.com",
            "QA": "qa-manager@krnl.com",
            "DevOps": "devops-manager@krnl.com",
            "Data Science": "data-manager@krnl.com",
            "Marketing": "marketing-manager@krnl.com",
            "Sales": "sales-manager@krnl.com",
            "HR": "hr-manager@krnl.com",
            "Finance": "finance-manager@krnl.com"
        }
        
        return manager_emails.get(department, "manager@krnl.com")
    
    def _format_time(self, iso_time: str) -> str:
        """Format ISO time string to readable format"""
        if not iso_time:
            return "TBD"
        
        try:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return iso_time
    
    async def _store_notification(self, employee_id: uuid.UUID, 
                                notification_type: str, recipient: str,
                                subject: str, message: str) -> Dict[str, Any]:
        """Store notification in database"""
        try:
            db = next(get_db())
            try:
                notification = Notification(
                    employee_id=employee_id,
                    type=notification_type,
                    recipient=recipient,
                    subject=subject,
                    message=message,
                    status="sent"
                )
                
                db.add(notification)
                db.commit()
                db.refresh(notification)
                
                self.logger.info("Notification stored successfully",
                               notification_type=notification_type,
                               recipient=recipient)
                
                return {
                    "id": str(notification.id),
                    "employee_id": str(notification.employee_id),
                    "type": notification.type,
                    "recipient": notification.recipient,
                    "subject": notification.subject,
                    "status": notification.status,
                    "sent_at": notification.sent_at.isoformat()
                }
            except Exception as e:
                self.logger.error(f"Failed to store notification in database: {e}")
                db.rollback()
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"Failed to create database session for notification: {e}")
            # Return a mock response if database fails
            return {
                "id": str(uuid.uuid4()),
                "employee_id": str(employee_id),
                "type": notification_type,
                "recipient": recipient,
                "subject": subject,
                "status": "sent",
                "sent_at": datetime.utcnow().isoformat(),
                "note": "Stored in fallback mode due to database error"
            }