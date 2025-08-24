from sqlalchemy import Column, String, DateTime, Integer, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workflows = relationship("OnboardingWorkflow", back_populates="employee")
    system_account = relationship("SystemAccount", back_populates="employee")
    calendar_events = relationship("CalendarEvent", back_populates="employee")
    notifications = relationship("Notification", back_populates="employee")

class OnboardingWorkflow(Base):
    __tablename__ = "onboarding_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    status = Column(String(50), default='started')
    current_step = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="workflows")
    logs = relationship("AgentLog", back_populates="workflow")

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey('onboarding_workflows.id'), nullable=True)
    agent_type = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    status = Column(String(50), nullable=False)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("OnboardingWorkflow", back_populates="logs")

class SystemAccount(Base):
    __tablename__ = "system_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    permissions = Column(JSONB, default=list)
    status = Column(String(50), default='active')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="system_account")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    event_id = Column(String(255))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default='scheduled')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="calendar_events")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employees.id'), nullable=False)
    type = Column(String(50), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255))
    message = Column(Text, nullable=False)
    status = Column(String(50), default='sent')
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="notifications")