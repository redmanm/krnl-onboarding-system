from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uuid
import csv
import io
import json
from datetime import datetime

# Import our modules
from database import get_db, create_tables
from models import Employee, OnboardingWorkflow
import schemas
from orchestrator import OnboardingOrchestrator
import structlog

# Try to import audit service, but continue without it if not available
try:
    from logging_system import AuditTrailService
    AUDIT_SERVICE_AVAILABLE = True
except ImportError:
    AuditTrailService = None
    AUDIT_SERVICE_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(
    title="KRNL Onboarding System API",
    description="Multi-agent employee onboarding workflow system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
    expose_headers=["*"]
)

# Initialize logger first
logger = structlog.get_logger(component="api")

# Initialize services
try:
    orchestrator = OnboardingOrchestrator()
    logger.info("Orchestrator initialized successfully")
except Exception as e:
    logger.error("Failed to initialize orchestrator", error=str(e))
    # Initialize with a basic orchestrator that doesn't use Redis
    orchestrator = OnboardingOrchestrator(redis_url=None)
    logger.info("Orchestrator initialized without Redis")

try:
    if AUDIT_SERVICE_AVAILABLE:
        audit_service = AuditTrailService()
        logger.info("Audit service initialized successfully")
    else:
        audit_service = None
        logger.warning("Audit service not available - logging_system module not imported")
except Exception as e:
    logger.error("Failed to initialize audit service", error=str(e))
    audit_service = None
    # Try to import again to see specific error
    try:
        from logging_system import AuditTrailService
        audit_service = AuditTrailService()
        logger.info("Audit service initialized on retry")
    except Exception as retry_error:
        logger.error("Audit service retry failed", error=str(retry_error))
        audit_service = None

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("API server started")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "krnl-onboarding-api"
    }

# OPTIONS handler for CORS preflight requests
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    """Handle CORS preflight requests"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
            "Access-Control-Max-Age": "86400"
        }
    )

# Employee endpoints
@app.post("/api/v1/employees", response_model=Dict[str, Any], tags=["Employees"])
async def create_employee(employee_data: schemas.EmployeeCreate, 
                         background_tasks: BackgroundTasks):
    """Create a new employee and start onboarding workflow"""
    try:
        # Convert Pydantic model to dict for orchestrator
        employee_dict = {
            "name": employee_data.name,
            "email": employee_data.email,
            "role": employee_data.role,
            "department": employee_data.department,
            "start_date": employee_data.start_date.isoformat()
        }
        
        # Start onboarding workflow in background
        workflow_result = await orchestrator.start_onboarding_workflow(employee_dict)
        
        logger.info("Employee created and workflow started",
                   employee_email=employee_data.email,
                   workflow_id=workflow_result["workflow_id"])
        
        return {
            "message": "Employee created and onboarding started",
            "workflow_id": workflow_result["workflow_id"],
            "employee_id": workflow_result["employee_id"],
            "status": workflow_result["status"]
        }
        
    except Exception as e:
        logger.error("Failed to create employee", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/employees/bulk", response_model=Dict[str, Any], tags=["Employees"])
async def create_bulk_employees(employees_data: schemas.BulkEmployeeUpload):
    """Create multiple employees and start their onboarding workflows"""
    try:
        # Convert employees to dict format
        employees_list = []
        for emp in employees_data.employees:
            employees_list.append({
                "name": emp.name,
                "email": emp.email,
                "role": emp.role,
                "department": emp.department,
                "start_date": emp.start_date.isoformat()
            })
        
        # Process in bulk
        result = await orchestrator.process_bulk_employees(employees_list)
        
        logger.info("Bulk employee processing completed",
                   total=result["total_processed"],
                   successful=result["successful"],
                   failed=result["failed"])
        
        return result
        
    except Exception as e:
        logger.error("Bulk employee processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/employees/upload-csv", response_model=Dict[str, Any], tags=["Employees"])
async def upload_employee_csv(file: UploadFile = File(...)):
    """Upload employee data via CSV file"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        employees_data = []
        
        for row in csv_reader:
            try:
                employee_data = {
                    "name": row.get("name", "").strip(),
                    "email": row.get("email", "").strip(),
                    "role": row.get("role", "").strip(),
                    "department": row.get("department", "").strip(),
                    "start_date": row.get("start_date", "").strip()
                }
                
                # Basic validation
                if not all([employee_data["name"], employee_data["email"], 
                           employee_data["role"], employee_data["department"],
                           employee_data["start_date"]]):
                    continue
                
                employees_data.append(employee_data)
                
            except Exception as e:
                logger.warning("Skipped invalid CSV row", error=str(e), row=row)
        
        if not employees_data:
            raise HTTPException(status_code=400, detail="No valid employee data found in CSV")
        
        # Process employees
        result = await orchestrator.process_bulk_employees(employees_data)
        
        return {
            "message": f"Processed {len(employees_data)} employees from CSV",
            "filename": file.filename,
            **result
        }
        
    except Exception as e:
        logger.error("CSV upload failed", filename=file.filename, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/employees", response_model=List[schemas.EmployeeWithStatus], tags=["Employees"])
async def list_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all employees with their onboarding status"""
    try:
        employees = db.query(Employee).offset(skip).limit(limit).all()
        
        result = []
        for employee in employees:
            # Get latest workflow for this employee
            workflow = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.employee_id == employee.id
            ).order_by(OnboardingWorkflow.created_at.desc()).first()
            
            employee_data = schemas.Employee.from_orm(employee).dict()
            employee_data.update({
                "workflow_status": workflow.status if workflow else None,
                "workflow_current_step": workflow.current_step if workflow else None,
                "account_created": False,  # Would check SystemAccount table
                "calendar_scheduled": False,  # Would check CalendarEvent table
                "notifications_sent": 0  # Would check Notification table
            })
            
            result.append(employee_data)
        
        return result
        
    except Exception as e:
        logger.error("Failed to list employees", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/employees/{employee_id}", response_model=Dict[str, Any], tags=["Employees"])
async def get_employee(employee_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get employee details with full onboarding trace"""
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get full trace
        if audit_service:
            trace = audit_service.get_employee_trace(employee_id)
        else:
            trace = {
                "employee": {
                    "id": str(employee_id),
                    "name": employee.name if employee else "Unknown",
                    "email": employee.email if employee else "Unknown"
                },
                "workflows": [],
                "summary": {
                    "completed_workflows": 0,
                    "failed_workflows": 0
                }
            }
        
        return trace
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get employee", employee_id=str(employee_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/employees/{employee_id}", response_model=Dict[str, Any], tags=["Employees"])
async def update_employee(employee_id: uuid.UUID, employee_data: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    """Update employee information"""
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Update employee fields
        employee.name = employee_data.name
        employee.email = employee_data.email
        employee.role = employee_data.role
        employee.department = employee_data.department
        employee.start_date = employee_data.start_date
        employee.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(employee)
        
        logger.info("Employee updated successfully", employee_id=str(employee_id), email=employee.email)
        
        return {
            "message": "Employee updated successfully",
            "employee_id": str(employee.id),
            "employee": {
                "id": str(employee.id),
                "name": employee.name,
                "email": employee.email,
                "role": employee.role,
                "department": employee.department,
                "start_date": employee.start_date.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update employee", employee_id=str(employee_id), error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/employees/{employee_id}", response_model=Dict[str, Any], tags=["Employees"])
async def delete_employee(employee_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete employee and all related data"""
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee_name = employee.name
        employee_email = employee.email
        
        # Delete related records (cascade should handle this, but let's be explicit)
        from models import OnboardingWorkflow, AgentLog, SystemAccount, CalendarEvent, Notification
        
        # Delete workflows
        workflows = db.query(OnboardingWorkflow).filter(OnboardingWorkflow.employee_id == employee_id).all()
        for workflow in workflows:
            # Delete agent logs for this workflow
            db.query(AgentLog).filter(AgentLog.workflow_id == workflow.id).delete()
            db.delete(workflow)
        
        # Delete system accounts
        db.query(SystemAccount).filter(SystemAccount.employee_id == employee_id).delete()
        
        # Delete calendar events
        db.query(CalendarEvent).filter(CalendarEvent.employee_id == employee_id).delete()
        
        # Delete notifications
        db.query(Notification).filter(Notification.employee_id == employee_id).delete()
        
        # Finally delete the employee
        db.delete(employee)
        db.commit()
        
        logger.info("Employee deleted successfully", 
                   employee_id=str(employee_id), 
                   name=employee_name, 
                   email=employee_email)
        
        return {
            "message": "Employee and all related data deleted successfully",
            "deleted_employee": {
                "id": str(employee_id),
                "name": employee_name,
                "email": employee_email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete employee", employee_id=str(employee_id), error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/employees/all", response_model=Dict[str, Any], tags=["Employees"])
async def delete_all_employees(confirm: bool = False, db: Session = Depends(get_db)):
    """Delete all employees and reset database (for demo purposes)"""
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="This is a destructive operation. Add ?confirm=true to proceed."
        )
    
    try:
        from models import OnboardingWorkflow, AgentLog, SystemAccount, CalendarEvent, Notification
        
        # Count before deletion
        employee_count = db.query(Employee).count()
        workflow_count = db.query(OnboardingWorkflow).count()
        
        # Delete all data in correct order (foreign key constraints)
        db.query(AgentLog).delete()
        db.query(Notification).delete()
        db.query(CalendarEvent).delete()
        db.query(SystemAccount).delete()
        db.query(OnboardingWorkflow).delete()
        db.query(Employee).delete()
        
        db.commit()
        
        logger.info("All employee data deleted", 
                   deleted_employees=employee_count,
                   deleted_workflows=workflow_count)
        
        return {
            "message": "All employee data deleted successfully",
            "deleted_counts": {
                "employees": employee_count,
                "workflows": workflow_count
            }
        }
        
    except Exception as e:
        logger.error("Failed to delete all employees", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Workflow endpoints
@app.get("/api/v1/workflows/{workflow_id}", response_model=Dict[str, Any], tags=["Workflows"])
async def get_workflow_status(workflow_id: uuid.UUID):
    """Get workflow status and detailed trace"""
    try:
        workflow_status = await orchestrator.get_workflow_status(workflow_id)
        return workflow_status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to get workflow status", workflow_id=str(workflow_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflows/{workflow_id}/trace", response_model=Dict[str, Any], tags=["Workflows"])
async def get_workflow_trace(workflow_id: uuid.UUID):
    """Get detailed workflow trace for auditing"""
    try:
        if audit_service:
            trace = audit_service.get_workflow_trace(workflow_id)
        else:
            trace = {
                "workflow_id": str(workflow_id),
                "trace": [],
                "summary": {
                    "total_steps": 0,
                    "completed_steps": 0,
                    "failed_steps": 0
                }
            }
        return trace
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to get workflow trace", workflow_id=str(workflow_id), error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard endpoints
@app.get("/api/v1/dashboard/stats", response_model=Dict[str, Any], tags=["Dashboard"])
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = await orchestrator.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error("Failed to get dashboard stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dashboard/recent-activity", response_model=Dict[str, Any], tags=["Dashboard"])
async def get_recent_activity(db: Session = Depends(get_db)):
    """Get recent onboarding activity"""
    try:
        # Get recent workflows
        recent_workflows = db.query(OnboardingWorkflow).order_by(
            OnboardingWorkflow.created_at.desc()
        ).limit(10).all()
        
        activity = []
        for workflow in recent_workflows:
            employee = db.query(Employee).filter(
                Employee.id == workflow.employee_id
            ).first()
            
            if employee:
                activity.append({
                    "workflow_id": str(workflow.id),
                    "employee_name": employee.name,
                    "employee_email": employee.email,
                    "status": workflow.status,
                    "current_step": workflow.current_step,
                    "created_at": workflow.created_at.isoformat(),
                    "updated_at": workflow.updated_at.isoformat()
                })
        
        return {"recent_activity": activity}
        
    except Exception as e:
        logger.error("Failed to get recent activity", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Audit and logging endpoints
@app.get("/api/v1/audit/agent-performance/{agent_type}", response_model=Dict[str, Any], tags=["Audit"])
async def get_agent_performance(agent_type: str, days: int = 7, db: Session = Depends(get_db)):
    """Get performance metrics for a specific agent"""
    try:
        if audit_service:
            logger.debug("Using audit service for agent performance", agent_type=agent_type)
            metrics = audit_service.get_agent_performance_metrics(agent_type, days)
        else:
            logger.debug("Using direct database query for agent performance", agent_type=agent_type)
            # Fallback: direct database query
            from datetime import datetime, timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            from models import AgentLog
            logs = db.query(AgentLog).filter(
                AgentLog.agent_type == agent_type,
                AgentLog.created_at >= start_date
            ).all()
            
            successful = [log for log in logs if log.status == "success"]
            failed = [log for log in logs if log.status == "failed"]
            
            execution_times = [log.execution_time_ms for log in successful if log.execution_time_ms]
            
            metrics = {
                "agent_type": agent_type,
                "period_days": days,
                "metrics": {
                    "total_executions": len(logs),
                    "successful_executions": len(successful),
                    "failed_executions": len(failed),
                    "success_rate": (len(successful) / len(logs) * 100) if logs else 0,
                    "average_execution_time_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
                    "min_execution_time_ms": min(execution_times) if execution_times else 0,
                    "max_execution_time_ms": max(execution_times) if execution_times else 0
                },
                "data_source": "direct_database_query"
            }
        
        logger.info("Agent performance retrieved", 
                   agent_type=agent_type,
                   total_executions=metrics.get("metrics", {}).get("total_executions", 0))
        
        return metrics
    except Exception as e:
        logger.error("Failed to get agent performance", agent_type=agent_type, error=str(e))
        # Return empty metrics as last resort
        return {
            "agent_type": agent_type,
            "metrics": {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "success_rate": 0.0,
                "average_execution_time_ms": 0
            },
            "error": str(e),
            "data_source": "fallback_empty"
        }

@app.get("/api/v1/audit/system-health", response_model=Dict[str, Any], tags=["Audit"])
async def get_system_health(db: Session = Depends(get_db)):
    """Get system health report"""
    try:
        if audit_service:
            logger.debug("Using audit service for system health")
            health_report = audit_service.get_system_health_report()
        else:
            logger.debug("Using direct database query for system health")
            # Fallback: direct database query
            from datetime import datetime, timedelta
            from models import AgentLog, OnboardingWorkflow
            
            # Last 24 hours
            start_time = datetime.utcnow() - timedelta(hours=24)
            
            recent_logs = db.query(AgentLog).filter(
                AgentLog.created_at >= start_time
            ).all()
            
            recent_workflows = db.query(OnboardingWorkflow).filter(
                OnboardingWorkflow.created_at >= start_time
            ).all()
            
            # Calculate metrics
            total_workflows = len(recent_workflows)
            completed_workflows = len([w for w in recent_workflows if w.status == "completed"])
            failed_workflows = len([w for w in recent_workflows if w.status == "failed"])
            
            # Agent metrics
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
            
            health_report = {
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
                "system_status": "healthy" if (completed_workflows / max(total_workflows, 1)) >= 0.9 else "degraded",
                "data_source": "direct_database_query"
            }
        
        return health_report
    except Exception as e:
        logger.error("Failed to get system health", error=str(e))
        return {
            "system_status": "unknown",
            "timestamp": datetime.utcnow().isoformat(),
            "workflow_metrics": {
                "total_workflows": 0,
                "completed_workflows": 0,
                "failed_workflows": 0,
                "success_rate": 0.0
            },
            "agent_metrics": {},
            "error": str(e),
            "data_source": "fallback_empty"
        }

@app.post("/api/v1/audit/search-logs", response_model=Dict[str, Any], tags=["Audit"])
async def search_logs(filters: Dict[str, Any], db: Session = Depends(get_db)):
    """Search audit logs with filters"""
    try:
        if audit_service:
            logger.debug("Using audit service for log search", filters=filters)
            search_results = audit_service.search_logs(filters)
        else:
            logger.debug("Using direct database query for log search", filters=filters)
            # Fallback: direct database query
            from models import AgentLog
            from datetime import datetime
            
            query = db.query(AgentLog)
            
            # Apply filters
            if "workflow_id" in filters:
                from uuid import UUID
                query = query.filter(AgentLog.workflow_id == UUID(filters["workflow_id"]))
            
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
            
            search_results = {
                "filters": filters,
                "result_count": len(logs),
                "logs": [
                    {
                        "id": str(log.id),
                        "workflow_id": str(log.workflow_id) if log.workflow_id else None,
                        "agent_type": log.agent_type,
                        "action": log.action,
                        "status": log.status,
                        "execution_time_ms": log.execution_time_ms,
                        "error_message": log.error_message,
                        "created_at": log.created_at.isoformat()
                    }
                    for log in logs
                ],
                "data_source": "direct_database_query"
            }
        
        return search_results
    except Exception as e:
        logger.error("Failed to search logs", filters=filters, error=str(e))
        return {
            "logs": [],
            "result_count": 0,
            "error": str(e),
            "data_source": "fallback_empty",
            "message": "Log search failed - check database connectivity"
        }

# Agent communication endpoints (for A2A)
@app.post("/api/v1/agents/{agent_name}/a2a", tags=["Agent Communication"])
async def handle_a2a_message(agent_name: str, message: Dict[str, Any]):
    """Handle agent-to-agent communication messages"""
    try:
        # This would route to appropriate agent based on agent_name
        # For now, just log the message
        logger.info("A2A message received", 
                   agent_name=agent_name, 
                   message_id=message.get("id"),
                   method=message.get("method"))
        
        return {"status": "received", "agent": agent_name}
        
    except Exception as e:
        logger.error("Failed to handle A2A message", 
                    agent_name=agent_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/{agent_name}/health", tags=["Agent Communication"])
async def agent_health_check(agent_name: str):
    """Health check for individual agents"""
    return {
        "status": "healthy",
        "agent": agent_name,
        "timestamp": datetime.utcnow().isoformat()
    }

# Debug endpoint for testing audit logs
@app.post("/api/v1/debug/create-test-log", tags=["Debug"])
async def create_test_agent_log(agent_type: str = "test", db: Session = Depends(get_db)):
    """Create a test agent log entry for debugging"""
    try:
        from models import AgentLog, OnboardingWorkflow
        import uuid
        
        # Find or create a test workflow
        test_workflow = db.query(OnboardingWorkflow).first()
        if not test_workflow:
            return {"error": "No workflows found. Create an employee first."}
        
        # Create test log entry
        test_log = AgentLog(
            workflow_id=test_workflow.id,
            agent_type=agent_type,
            action="test_action",
            input_data={"test": "data"},
            output_data={"result": "success"},
            status="success",
            execution_time_ms=150
        )
        
        db.add(test_log)
        db.commit()
        db.refresh(test_log)
        
        logger.info("Test agent log created", 
                   log_id=str(test_log.id),
                   agent_type=agent_type)
        
        return {
            "message": "Test log created successfully",
            "log_id": str(test_log.id),
            "workflow_id": str(test_workflow.id),
            "agent_type": agent_type
        }
        
    except Exception as e:
        logger.error("Failed to create test log", error=str(e))
        return {"error": str(e)}

@app.get("/api/v1/debug/agent-logs-count", tags=["Debug"])
async def get_agent_logs_count(db: Session = Depends(get_db)):
    """Get count of agent logs for debugging"""
    try:
        from models import AgentLog
        
        total_logs = db.query(AgentLog).count()
        
        # Count by agent type
        agent_counts = {}
        agents = ['validator', 'account_setup', 'scheduler', 'notifier']
        
        for agent_type in agents:
            count = db.query(AgentLog).filter(AgentLog.agent_type == agent_type).count()
            agent_counts[agent_type] = count
        
        return {
            "total_logs": total_logs,
            "agent_counts": agent_counts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get agent logs count", error=str(e))
        return {"error": str(e)}

@app.post("/api/v1/debug/test-orchestrator", tags=["Debug"])
async def test_orchestrator_execution():
    """Test orchestrator execution with detailed logging"""
    try:
        # Create test employee data
        test_employee_data = {
            "name": "Orchestrator Test User",
            "email": "orchestrator.test@krnl.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "start_date": "2024-02-01"
        }
        
        logger.info("Starting orchestrator test", employee_data=test_employee_data)
        
        # Execute workflow through orchestrator
        result = await orchestrator.start_onboarding_workflow(test_employee_data)
        
        logger.info("Orchestrator test completed", 
                   workflow_id=result.get("workflow_id"),
                   status=result.get("status"))
        
        return {
            "message": "Orchestrator test completed",
            "result": result,
            "test_type": "full_workflow"
        }
        
    except Exception as e:
        logger.error("Orchestrator test failed", error=str(e))
        return {"error": str(e), "test_type": "full_workflow"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error("Internal server error", path=str(request.url), error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")