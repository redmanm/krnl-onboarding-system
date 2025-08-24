import json
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import AgentLog, OnboardingWorkflow, Employee
import uuid

class TraceabilityLogger:
    """Enhanced logging system with traceability and audit capabilities"""
    
    def __init__(self):
        self.logger = structlog.get_logger(component="traceability")
        self._configure_structlog()
    
    def _configure_structlog(self):
        """Configure structlog for consistent logging"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def create_trace_context(self, workflow_id: uuid.UUID, 
                           employee_id: uuid.UUID) -> Dict[str, Any]:
        """Create tracing context for a workflow"""
        return {
            "workflow_id": str(workflow_id),
            "employee_id": str(employee_id),
            "trace_start": datetime.utcnow().isoformat()
        }
    
    def log_agent_start(self, context: Dict[str, Any], agent_type: str, 
                       action: str, input_data: Dict[str, Any]):
        """Log when an agent starts processing"""
        self.logger.info(
            "Agent processing started",
            **context,
            agent_type=agent_type,
            action=action,
            input_size=len(json.dumps(input_data)),
            start_time=datetime.utcnow().isoformat()
        )
    
    def log_agent_completion(self, context: Dict[str, Any], agent_type: str,
                           action: str, output_data: Dict[str, Any], 
                           execution_time_ms: int):
        """Log successful agent completion"""
        self.logger.info(
            "Agent processing completed",
            **context,
            agent_type=agent_type,
            action=action,
            output_size=len(json.dumps(output_data)),
            execution_time_ms=execution_time_ms,
            completion_time=datetime.utcnow().isoformat()
        )
    
    def log_agent_error(self, context: Dict[str, Any], agent_type: str,
                       action: str, error: str, execution_time_ms: int):
        """Log agent processing error"""
        self.logger.error(
            "Agent processing failed",
            **context,
            agent_type=agent_type,
            action=action,
            error=error,
            execution_time_ms=execution_time_ms,
            failure_time=datetime.utcnow().isoformat()
        )
    
    def log_workflow_step(self, context: Dict[str, Any], step_name: str, 
                         status: str, details: Dict[str, Any] = None):
        """Log workflow step progression"""
        self.logger.info(
            "Workflow step update",
            **context,
            step_name=step_name,
            status=status,
            details=details or {},
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_a2a_communication(self, context: Dict[str, Any], 
                            source_agent: str, target_agent: str,
                            method: str, success: bool, 
                            response_time_ms: int = None):
        """Log agent-to-agent communication"""
        self.logger.info(
            "A2A communication",
            **context,
            source_agent=source_agent,
            target_agent=target_agent,
            method=method,
            success=success,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow().isoformat()
        )

class AuditTrailService:
    """Service for querying and analyzing audit trails"""
    
    def __init__(self):
        self.logger = structlog.get_logger(component="audit_trail")
    
    def get_workflow_trace(self, workflow_id: uuid.UUID) -> Dict[str, Any]:
        """Get complete trace for a workflow"""
        db = next(get_db())
        try:
            # Get workflow details
            workflow = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.id == workflow_id
            ).first()
            
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Get employee details
            employee = db.query(Employee).filter(
                Employee.id == workflow.employee_id
            ).first()
            
            # Get all logs for this workflow
            logs = db.query(AgentLog).filter(
                AgentLog.workflow_id == workflow_id
            ).order_by(AgentLog.created_at).all()
            
            # Calculate metrics
            total_execution_time = sum(log.execution_time_ms or 0 for log in logs)
            successful_steps = len([log for log in logs if log.status == "success"])
            failed_steps = len([log for log in logs if log.status == "failed"])
            
            return {
                "workflow": {
                    "id": str(workflow.id),
                    "status": workflow.status,
                    "current_step": workflow.current_step,
                    "created_at": workflow.created_at.isoformat(),
                    "updated_at": workflow.updated_at.isoformat()
                },
                "employee": {
                    "id": str(employee.id),
                    "name": employee.name,
                    "email": employee.email,
                    "role": employee.role,
                    "department": employee.department
                } if employee else None,
                "metrics": {
                    "total_steps": len(logs),
                    "successful_steps": successful_steps,
                    "failed_steps": failed_steps,
                    "total_execution_time_ms": total_execution_time,
                    "average_step_time_ms": total_execution_time // max(len(logs), 1)
                },
                "timeline": [
                    {
                        "timestamp": log.created_at.isoformat(),
                        "agent_type": log.agent_type,
                        "action": log.action,
                        "status": log.status,
                        "execution_time_ms": log.execution_time_ms,
                        "input_data": log.input_data,
                        "output_data": log.output_data,
                        "error_message": log.error_message
                    }
                    for log in logs
                ]
            }
        finally:
            db.close()
    
    def get_employee_trace(self, employee_id: uuid.UUID) -> Dict[str, Any]:
        """Get all traces for an employee across workflows"""
        db = next(get_db())
        try:
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            if not employee:
                raise ValueError(f"Employee {employee_id} not found")
            
            workflows = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.employee_id == employee_id
            ).order_by(OnboardingWorkflow.created_at).all()
            
            traces = []
            for workflow in workflows:
                try:
                    trace = self.get_workflow_trace(workflow.id)
                    traces.append(trace)
                except Exception as e:
                    self.logger.error("Failed to get workflow trace",
                                    workflow_id=str(workflow.id), error=str(e))
            
            return {
                "employee": {
                    "id": str(employee.id),
                    "name": employee.name,
                    "email": employee.email,
                    "role": employee.role,
                    "department": employee.department
                },
                "workflows": traces,
                "summary": {
                    "total_workflows": len(workflows),
                    "completed_workflows": len([w for w in workflows if w.status == "completed"]),
                    "failed_workflows": len([w for w in workflows if w.status == "failed"])
                }
            }
        finally:
            db.close()
    
    def get_agent_performance_metrics(self, agent_type: str, 
                                    days: int = 7) -> Dict[str, Any]:
        """Get performance metrics for a specific agent"""
        db = next(get_db())
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            logs = db.query(AgentLog).filter(
                AgentLog.agent_type == agent_type,
                AgentLog.created_at >= start_date
            ).all()
            
            if not logs:
                return {"agent_type": agent_type, "metrics": {}, "message": "No data available"}
            
            successful = [log for log in logs if log.status == "success"]
            failed = [log for log in logs if log.status == "failed"]
            
            execution_times = [log.execution_time_ms for log in successful if log.execution_time_ms]
            
            return {
                "agent_type": agent_type,
                "period_days": days,
                "metrics": {
                    "total_executions": len(logs),
                    "successful_executions": len(successful),
                    "failed_executions": len(failed),
                    "success_rate": (len(successful) / len(logs)) * 100,
                    "average_execution_time_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
                    "min_execution_time_ms": min(execution_times) if execution_times else 0,
                    "max_execution_time_ms": max(execution_times) if execution_times else 0,
                    "total_execution_time_ms": sum(execution_times)
                },
                "error_analysis": self._analyze_errors(failed)
            }
        finally:
            db.close()
    
    def _analyze_errors(self, failed_logs: List) -> Dict[str, Any]:
        """Analyze error patterns in failed logs"""
        if not failed_logs:
            return {"total_errors": 0, "error_types": {}}
        
        error_types = {}
        for log in failed_logs:
            error_msg = log.error_message or "Unknown error"
            # Simple error categorization
            if "validation" in error_msg.lower():
                category = "validation_error"
            elif "database" in error_msg.lower() or "connection" in error_msg.lower():
                category = "database_error"
            elif "timeout" in error_msg.lower():
                category = "timeout_error"
            elif "permission" in error_msg.lower() or "unauthorized" in error_msg.lower():
                category = "permission_error"
            else:
                category = "other_error"
            
            if category not in error_types:
                error_types[category] = {"count": 0, "examples": []}
            
            error_types[category]["count"] += 1
            if len(error_types[category]["examples"]) < 3:
                error_types[category]["examples"].append({
                    "timestamp": log.created_at.isoformat(),
                    "message": error_msg
                })
        
        return {
            "total_errors": len(failed_logs),
            "error_types": error_types
        }
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate system health report based on recent activity"""
        db = next(get_db())
        try:
            # Last 24 hours
            start_time = datetime.utcnow() - timedelta(hours=24)
            
            recent_logs = db.query(AgentLog).filter(
                AgentLog.created_at >= start_time
            ).all()
            
            recent_workflows = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.created_at >= start_time
            ).all()
            
            # Calculate system metrics
            total_workflows = len(recent_workflows)
            completed_workflows = len([w for w in recent_workflows if w.status == "completed"])
            failed_workflows = len([w for w in recent_workflows if w.status == "failed"])
            
            # Agent performance
            agent_stats = {}
            for log in recent_logs:
                agent_type = log.agent_type
                if agent_type not in agent_stats:
                    agent_stats[agent_type] = {"success": 0, "failure": 0, "total_time": 0}
                
                if log.status == "success":
                    agent_stats[agent_type]["success"] += 1
                else:
                    agent_stats[agent_type]["failure"] += 1
                
                if log.execution_time_ms:
                    agent_stats[agent_type]["total_time"] += log.execution_time_ms
            
            return {
                "report_period": "24_hours",
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_metrics": {
                    "total_workflows": total_workflows,
                    "completed_workflows": completed_workflows,
                    "failed_workflows": failed_workflows,
                    "success_rate": (completed_workflows / max(total_workflows, 1)) * 100
                },
                "agent_metrics": {
                    agent_type: {
                        **stats,
                        "success_rate": (stats["success"] / max(stats["success"] + stats["failure"], 1)) * 100,
                        "average_execution_time": stats["total_time"] / max(stats["success"], 1)
                    }
                    for agent_type, stats in agent_stats.items()
                },
                "system_status": "healthy" if (completed_workflows / max(total_workflows, 1)) >= 0.9 else "degraded"
            }
        finally:
            db.close()
    
    def search_logs(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search logs with various filters"""
        db = next(get_db())
        try:
            query = db.query(AgentLog)
            
            # Apply filters
            if "workflow_id" in filters:
                query = query.filter(AgentLog.workflow_id == filters["workflow_id"])
            
            if "agent_type" in filters:
                query = query.filter(AgentLog.agent_type == filters["agent_type"])
            
            if "status" in filters:
                query = query.filter(AgentLog.status == filters["status"])
            
            if "start_date" in filters:
                start_date = datetime.fromisoformat(filters["start_date"])
                query = query.filter(AgentLog.created_at >= start_date)
            
            if "end_date" in filters:
                end_date = datetime.fromisoformat(filters["end_date"])
                query = query.filter(AgentLog.created_at <= end_date)
            
            # Execute query with limit
            limit = filters.get("limit", 100)
            logs = query.order_by(AgentLog.created_at.desc()).limit(limit).all()
            
            return {
                "filters": filters,
                "result_count": len(logs),
                "logs": [
                    {
                        "id": str(log.id),
                        "workflow_id": str(log.workflow_id),
                        "agent_type": log.agent_type,
                        "action": log.action,
                        "status": log.status,
                        "execution_time_ms": log.execution_time_ms,
                        "error_message": log.error_message,
                        "created_at": log.created_at.isoformat()
                    }
                    for log in logs
                ]
            }
        finally:
            db.close()