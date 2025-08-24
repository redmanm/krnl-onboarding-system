import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

import structlog
from database import get_db
from models import Employee, OnboardingWorkflow, AgentLog
from agents.validator_agent import ValidatorAgent
from agents.account_setup_agent import AccountSetupAgent
from agents.scheduler_agent import SchedulerAgent
from agents.notifier_agent import NotifierAgent
from communication.a2a_system import A2ACommunicationBus
import schemas

class WorkflowStatus(Enum):
    STARTED = "started"
    VALIDATION_IN_PROGRESS = "validation_in_progress"
    VALIDATION_COMPLETED = "validation_completed"
    ACCOUNT_SETUP_IN_PROGRESS = "account_setup_in_progress"
    ACCOUNT_SETUP_COMPLETED = "account_setup_completed"
    SCHEDULING_IN_PROGRESS = "scheduling_in_progress"
    SCHEDULING_COMPLETED = "scheduling_completed"
    NOTIFICATION_IN_PROGRESS = "notification_in_progress"
    NOTIFICATION_COMPLETED = "notification_completed"
    COMPLETED = "completed"
    FAILED = "failed"

class OnboardingOrchestrator:
    """Orchestrates the multi-agent onboarding workflow"""
    
    def __init__(self, redis_url: str = "redis://redis:6379"):
        self.logger = structlog.get_logger(component="orchestrator")
        
        # Initialize communication bus with error handling
        self.communication_bus = None
        if redis_url:
            try:
                self.communication_bus = A2ACommunicationBus(redis_url)
                # Test the connection
                import redis
                test_client = redis.from_url(redis_url)
                test_client.ping()
                self.logger.info("A2A communication bus initialized successfully")
            except Exception as e:
                self.logger.warning("Failed to initialize A2A communication bus, proceeding without it", 
                                  error=str(e),
                                  redis_url=redis_url)
                self.communication_bus = None
        else:
            self.logger.info("Redis URL not provided, skipping A2A communication bus")
        
        # Initialize agents with simplified communication
        try:
            self.validator_agent = ValidatorAgent()
            self.account_setup_agent = AccountSetupAgent(self.communication_bus)
            self.scheduler_agent = SchedulerAgent()
            self.notifier_agent = NotifierAgent()
            
            # Validate all agents were created properly
            agents_status = {
                "validator": self.validator_agent is not None,
                "account_setup": self.account_setup_agent is not None,
                "scheduler": self.scheduler_agent is not None,
                "notifier": self.notifier_agent is not None
            }
            
            failed_agents = [name for name, status in agents_status.items() if not status]
            if failed_agents:
                raise Exception(f"Failed to initialize agents: {failed_agents}")
            
            self.logger.info("All agents initialized successfully",
                           a2a_enabled=self.communication_bus is not None,
                           agents_status=agents_status)
                           
            # Validate agent types
            for agent_name, agent in [("validator", self.validator_agent), 
                                     ("account_setup", self.account_setup_agent),
                                     ("scheduler", self.scheduler_agent), 
                                     ("notifier", self.notifier_agent)]:
                if not hasattr(agent, 'agent_type'):
                    self.logger.warning(f"Agent {agent_name} missing agent_type attribute")
                if not hasattr(agent, 'execute'):
                    raise Exception(f"Agent {agent_name} missing execute method")
                    
        except Exception as e:
            self.logger.error("Failed to initialize agents", error=str(e))
            raise
        
        # Agent execution order
        self.workflow_steps = [
            {
                "name": "validation",
                "agent": self.validator_agent,
                "status": WorkflowStatus.VALIDATION_IN_PROGRESS,
                "completion_status": WorkflowStatus.VALIDATION_COMPLETED
            },
            {
                "name": "account_setup", 
                "agent": self.account_setup_agent,
                "status": WorkflowStatus.ACCOUNT_SETUP_IN_PROGRESS,
                "completion_status": WorkflowStatus.ACCOUNT_SETUP_COMPLETED
            },
            {
                "name": "scheduling",
                "agent": self.scheduler_agent,
                "status": WorkflowStatus.SCHEDULING_IN_PROGRESS,
                "completion_status": WorkflowStatus.SCHEDULING_COMPLETED
            },
            {
                "name": "notification",
                "agent": self.notifier_agent,
                "status": WorkflowStatus.NOTIFICATION_IN_PROGRESS,
                "completion_status": WorkflowStatus.NOTIFICATION_COMPLETED
            }
        ]
    
    async def start_onboarding_workflow(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start the complete onboarding workflow for an employee"""
        workflow_id = None
        
        self.logger.info("Starting onboarding workflow",
                        employee_email=employee_data.get("email"))
        
        try:
            # Create employee record
            employee = await self._create_employee_record(employee_data)
            employee_id = employee.id
            
            # Create workflow record
            workflow = await self._create_workflow_record(employee_id)
            workflow_id = workflow.id
            
            self.logger.info("Created workflow record",
                           workflow_id=str(workflow_id),
                           employee_id=str(employee_id))
            
            # Execute workflow steps
            workflow_result = await self._execute_workflow(workflow.id, employee_data, employee_id)
            
            # Update final workflow status
            await self._update_workflow_status(workflow.id, WorkflowStatus.COMPLETED)
            
            result = {
                "workflow_id": str(workflow.id),
                "employee_id": str(employee_id),
                "status": "completed",
                "employee_data": {
                    "name": employee.name,
                    "email": employee.email,
                    "role": employee.role,
                    "department": employee.department,
                    "start_date": employee.start_date.isoformat()
                },
                "workflow_results": workflow_result,
                "completion_time": datetime.utcnow().isoformat()
            }
            
            self.logger.info("Onboarding workflow completed successfully",
                           workflow_id=str(workflow.id),
                           employee_id=str(employee_id))
            
            return result
            
        except Exception as e:
            if workflow_id:
                await self._update_workflow_status(workflow_id, WorkflowStatus.FAILED)
            self.logger.error("Onboarding workflow failed",
                            workflow_id=str(workflow_id) if workflow_id else "unknown",
                            error=str(e),
                            employee_email=employee_data.get("email"))
            raise
    
    async def _execute_workflow(self, workflow_id: uuid.UUID, 
                              employee_data: Dict[str, Any],
                              employee_id: uuid.UUID) -> Dict[str, Any]:
        """Execute all workflow steps in sequence"""
        workflow_results = {}
        accumulated_data = {"employee_data": employee_data, "employee_id": employee_id}
        
        self.logger.info("Starting workflow execution",
                       workflow_id=str(workflow_id),
                       total_steps=len(self.workflow_steps))
        
        for i, step in enumerate(self.workflow_steps, 1):
            step_name = step["name"]
            agent = step["agent"]
            
            self.logger.info("Executing workflow step",
                           workflow_id=str(workflow_id),
                           step=step_name,
                           step_number=f"{i}/{len(self.workflow_steps)}")
            
            # Update workflow status
            await self._update_workflow_status(workflow_id, step["status"])
            
            try:
                # Validate agent before execution
                if agent is None:
                    raise ValueError(f"Agent for step '{step_name}' is None")
                
                if not hasattr(agent, 'execute'):
                    raise ValueError(f"Agent for step '{step_name}' does not have execute method")
                
                # Execute agent with accumulated data
                self.logger.info("Calling agent execute method",
                               workflow_id=str(workflow_id),
                               agent_type=getattr(agent, 'agent_type', 'unknown'),
                               input_data_keys=list(accumulated_data.keys()))
                
                step_result = await agent.execute(workflow_id, accumulated_data)
                
                self.logger.info("Agent execute method completed",
                               workflow_id=str(workflow_id),
                               agent_type=getattr(agent, 'agent_type', 'unknown'),
                               result_type=type(step_result).__name__,
                               result_keys=list(step_result.keys()) if isinstance(step_result, dict) else "not_dict")
                
                # Store step result
                workflow_results[step_name] = step_result
                
                # Update accumulated data for next step
                accumulated_data[f"{step_name}_result"] = step_result
                
                # Special handling for specific step results
                if step_name == "account_setup" and step_result:
                    accumulated_data["account_data"] = step_result.get("account_details", {})
                    accumulated_data["username"] = step_result.get("username", "")
                    accumulated_data["permissions"] = step_result.get("permissions", [])
                
                if step_name == "scheduling" and step_result:
                    accumulated_data["calendar_data"] = {
                        "events": step_result.get("events", []),
                        "scheduled_events": step_result.get("events", [])
                    }
                
                # Update completion status
                await self._update_workflow_status(workflow_id, step["completion_status"])
                
                self.logger.info("Workflow step completed successfully",
                               workflow_id=str(workflow_id),
                               step=step_name,
                               step_number=f"{i}/{len(self.workflow_steps)}")
                
            except Exception as e:
                self.logger.error("Workflow step failed",
                                workflow_id=str(workflow_id),
                                step=step_name,
                                step_number=f"{i}/{len(self.workflow_steps)}",
                                error=str(e),
                                error_type=type(e).__name__)
                
                await self._update_workflow_status(workflow_id, WorkflowStatus.FAILED)
                raise
        
        self.logger.info("All workflow steps completed successfully",
                       workflow_id=str(workflow_id),
                       total_steps=len(self.workflow_steps))
        
        return workflow_results
    
    async def _create_employee_record(self, employee_data: Dict[str, Any]) -> Employee:
        """Create employee record in database"""
        try:
            db = next(get_db())
            try:
                employee = Employee(
                    name=employee_data["name"],
                    email=employee_data["email"],
                    role=employee_data["role"],
                    department=employee_data["department"],
                    start_date=datetime.fromisoformat(employee_data["start_date"]).date(),
                    status="onboarding"
                )
                
                db.add(employee)
                db.commit()
                db.refresh(employee)
                
                self.logger.info("Employee record created",
                               employee_email=employee.email,
                               employee_id=str(employee.id))
                
                return employee
            except Exception as e:
                self.logger.error("Failed to create employee record", error=str(e))
                db.rollback()
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.error("Failed to create database session for employee creation", error=str(e))
            raise
    
    async def _create_workflow_record(self, employee_id: uuid.UUID) -> OnboardingWorkflow:
        """Create workflow record in database"""
        try:
            db = next(get_db())
            try:
                workflow = OnboardingWorkflow(
                    employee_id=employee_id,
                    status=WorkflowStatus.STARTED.value,
                    current_step="validation"
                )
                
                db.add(workflow)
                db.commit()
                db.refresh(workflow)
                
                self.logger.info("Workflow record created",
                               workflow_id=str(workflow.id),
                               employee_id=str(employee_id))
                
                return workflow
            except Exception as e:
                self.logger.error("Failed to create workflow record", error=str(e))
                db.rollback()
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.error("Failed to create database session for workflow creation", error=str(e))
            raise
    
    async def _update_workflow_status(self, workflow_id: uuid.UUID, status: WorkflowStatus):
        """Update workflow status in database"""
        try:
            db = next(get_db())
            try:
                workflow = db.query(OnboardingWorkflow).filter(
                    OnboardingWorkflow.id == workflow_id
                ).first()
                
                if workflow:
                    workflow.status = status.value
                    if status == WorkflowStatus.VALIDATION_IN_PROGRESS:
                        workflow.current_step = "validation"
                    elif status == WorkflowStatus.ACCOUNT_SETUP_IN_PROGRESS:
                        workflow.current_step = "account_setup"
                    elif status == WorkflowStatus.SCHEDULING_IN_PROGRESS:
                        workflow.current_step = "scheduling"
                    elif status == WorkflowStatus.NOTIFICATION_IN_PROGRESS:
                        workflow.current_step = "notification"
                    elif status == WorkflowStatus.COMPLETED:
                        workflow.current_step = "completed"
                    elif status == WorkflowStatus.FAILED:
                        workflow.current_step = "failed"
                    
                    db.commit()
                    
                    self.logger.debug("Workflow status updated",
                                    workflow_id=str(workflow_id),
                                    status=status.value,
                                    current_step=workflow.current_step)
                else:
                    self.logger.warning("Workflow not found for status update",
                                      workflow_id=str(workflow_id))
            except Exception as e:
                self.logger.error("Failed to update workflow status", error=str(e))
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            self.logger.error("Failed to create database session for workflow status update", error=str(e))
    
    async def get_workflow_status(self, workflow_id: uuid.UUID) -> Dict[str, Any]:
        """Get current workflow status and progress"""
        db = next(get_db())
        try:
            workflow = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.id == workflow_id
            ).first()
            
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Get employee data
            employee = db.query(Employee).filter(
                Employee.id == workflow.employee_id
            ).first()
            
            # Get logs
            logs = db.query(AgentLog).filter(
                AgentLog.workflow_id == workflow_id
            ).order_by(AgentLog.created_at).all()
            
            return {
                "workflow_id": str(workflow.id),
                "status": workflow.status,
                "current_step": workflow.current_step,
                "employee": {
                    "name": employee.name,
                    "email": employee.email,
                    "role": employee.role,
                    "department": employee.department
                } if employee else None,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "logs": [
                    {
                        "agent_type": log.agent_type,
                        "action": log.action,
                        "status": log.status,
                        "execution_time_ms": log.execution_time_ms,
                        "created_at": log.created_at.isoformat()
                    }
                    for log in logs
                ]
            }
        finally:
            db.close()
    
    async def process_bulk_employees(self, employees_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple employees in parallel"""
        self.logger.info("Starting bulk employee processing",
                        count=len(employees_data))
        
        # Create tasks for parallel processing
        tasks = [
            self.start_onboarding_workflow(employee_data)
            for employee_data in employees_data
        ]
        
        # Execute all workflows in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Categorize results
        successful = []
        failed = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    "employee_data": employees_data[i],
                    "error": str(result)
                })
            else:
                successful.append(result)
        
        return {
            "total_processed": len(employees_data),
            "successful": len(successful),
            "failed": len(failed),
            "successful_workflows": successful,
            "failed_workflows": failed
        }
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for dashboard"""
        db = next(get_db())
        try:
            total_employees = db.query(Employee).count()
            
            pending = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.status.in_([
                    WorkflowStatus.STARTED.value,
                    WorkflowStatus.VALIDATION_IN_PROGRESS.value,
                    WorkflowStatus.ACCOUNT_SETUP_IN_PROGRESS.value,
                    WorkflowStatus.SCHEDULING_IN_PROGRESS.value,
                    WorkflowStatus.NOTIFICATION_IN_PROGRESS.value
                ])
            ).count()
            
            completed = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.status == WorkflowStatus.COMPLETED.value
            ).count()
            
            failed = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.status == WorkflowStatus.FAILED.value
            ).count()
            
            return {
                "total_employees": total_employees,
                "pending_onboarding": pending,
                "completed_onboarding": completed,
                "failed_onboarding": failed,
                "success_rate": (completed / max(total_employees, 1)) * 100
            }
        finally:
            db.close()