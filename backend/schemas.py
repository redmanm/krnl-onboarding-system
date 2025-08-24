from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import uuid

# Employee schemas
class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    department: str
    start_date: date

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[date] = None
    status: Optional[str] = None

class Employee(EmployeeBase):
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Workflow schemas
class OnboardingWorkflowBase(BaseModel):
    status: str = "started"
    current_step: Optional[str] = None

class OnboardingWorkflowCreate(OnboardingWorkflowBase):
    employee_id: uuid.UUID

class OnboardingWorkflow(OnboardingWorkflowBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Agent Log schemas
class AgentLogBase(BaseModel):
    agent_type: str
    action: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None

class AgentLogCreate(AgentLogBase):
    workflow_id: uuid.UUID

class AgentLog(AgentLogBase):
    id: uuid.UUID
    workflow_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# System Account schemas
class SystemAccountBase(BaseModel):
    username: str
    permissions: List[str] = []
    status: str = "active"

class SystemAccountCreate(SystemAccountBase):
    employee_id: uuid.UUID

class SystemAccount(SystemAccountBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Calendar Event schemas
class CalendarEventBase(BaseModel):
    event_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str = "scheduled"

class CalendarEventCreate(CalendarEventBase):
    employee_id: uuid.UUID

class CalendarEvent(CalendarEventBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Notification schemas
class NotificationBase(BaseModel):
    type: str
    recipient: str
    subject: Optional[str] = None
    message: str
    status: str = "sent"

class NotificationCreate(NotificationBase):
    employee_id: uuid.UUID

class Notification(NotificationBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    sent_at: datetime

    class Config:
        from_attributes = True

# Bulk employee upload schema
class BulkEmployeeUpload(BaseModel):
    employees: List[EmployeeCreate]

# Dashboard response schemas
class EmployeeWithStatus(Employee):
    workflow_status: Optional[str] = None
    workflow_current_step: Optional[str] = None
    account_created: bool = False
    calendar_scheduled: bool = False
    notifications_sent: int = 0

class DashboardStats(BaseModel):
    total_employees: int
    pending_onboarding: int
    completed_onboarding: int
    in_progress: int
    failed: int

class WorkflowTrace(BaseModel):
    employee: Employee
    workflow: OnboardingWorkflow
    logs: List[AgentLog]
    system_account: Optional[SystemAccount]
    calendar_events: List[CalendarEvent]
    notifications: List[Notification]