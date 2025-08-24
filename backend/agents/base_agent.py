import asyncio
import time
import json
import structlog
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import AgentLog, OnboardingWorkflow
import uuid

class BaseAgent(ABC):
    """Base class for all agents with common functionality"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.logger = structlog.get_logger(agent_type=agent_type)
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return results"""
        pass
    
    async def execute(self, workflow_id: uuid.UUID, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with logging and error handling"""
        start_time = time.time()
        
        try:
            self.logger.info("Starting agent execution", 
                           workflow_id=str(workflow_id), 
                           agent_type=self.agent_type,
                           input_data_keys=list(input_data.keys()) if input_data else [])
            
            # Process the data
            result = await self.process(input_data)
            
            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            await self._log_execution(
                workflow_id, "process", input_data, result, 
                "success", None, execution_time
            )
            
            self.logger.info("Agent execution completed successfully", 
                           workflow_id=str(workflow_id),
                           agent_type=self.agent_type,
                           execution_time_ms=execution_time)
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = str(e)
            
            # Log failed execution
            try:
                await self._log_execution(
                    workflow_id, "process", input_data, None,
                    "failed", error_msg, execution_time
                )
            except Exception as log_error:
                self.logger.error("Failed to log execution failure", 
                                error=str(log_error))
            
            self.logger.error("Agent execution failed",
                            workflow_id=str(workflow_id),
                            agent_type=self.agent_type,
                            error=error_msg,
                            error_type=type(e).__name__,
                            execution_time_ms=execution_time)
            
            raise
    
    def _serialize_for_json(self, data):
        """Recursively serialize data for JSON storage"""
        if isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, dict):
            return {k: self._serialize_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_for_json(item) for item in data]
        elif hasattr(data, 'isoformat'):  # datetime objects
            return data.isoformat()
        else:
            return data
    
    async def _log_execution(self, workflow_id: uuid.UUID, 
                           action: str, input_data: Dict[str, Any], 
                           output_data: Optional[Dict[str, Any]], 
                           status: str, error_message: Optional[str], 
                           execution_time_ms: int):
        """Log agent execution to database"""
        try:
            # Always try to log, even if database fails
            self.logger.info("Attempting to log agent execution",
                           workflow_id=str(workflow_id),
                           agent_type=self.agent_type,
                           action=action,
                           status=status,
                           execution_time_ms=execution_time_ms)
            
            db = next(get_db())
            try:
                # Check if workflow exists first
                workflow_exists = db.query(OnboardingWorkflow).filter(
                    OnboardingWorkflow.id == workflow_id
                ).first() is not None
                
                # Serialize data to handle UUID and other non-JSON types
                safe_input_data = self._serialize_for_json(input_data or {})
                safe_output_data = self._serialize_for_json(output_data or {})
                
                log_entry = AgentLog(
                    workflow_id=workflow_id if workflow_exists else None,
                    agent_type=self.agent_type,
                    action=action,
                    input_data=safe_input_data,
                    output_data=safe_output_data,
                    status=status,
                    error_message=error_message,
                    execution_time_ms=execution_time_ms
                )
                
                db.add(log_entry)
                db.commit()
                
                self.logger.info("Agent execution logged successfully",
                                workflow_id=str(workflow_id),
                                agent_type=self.agent_type,
                                status=status,
                                workflow_exists=workflow_exists,
                                log_id=str(log_entry.id))
                
            except Exception as db_error:
                self.logger.error("Failed to log execution to database", 
                                 workflow_id=str(workflow_id),
                                 agent_type=self.agent_type,
                                 error=str(db_error),
                                 error_type=type(db_error).__name__)
                db.rollback()
                # Don't raise - logging failure shouldn't break workflow
            finally:
                db.close()
                
        except Exception as session_error:
            self.logger.error("Failed to create database session for logging", 
                             workflow_id=str(workflow_id),
                             agent_type=self.agent_type,
                             error=str(session_error),
                             error_type=type(session_error).__name__)
    
    async def update_workflow_step(self, workflow_id: uuid.UUID, step: str, status: str = None):
        """Update the current workflow step"""
        try:
            db = next(get_db())
            try:
                workflow = db.query(OnboardingWorkflow).filter(
                    OnboardingWorkflow.id == workflow_id
                ).first()
                
                if workflow:
                    workflow.current_step = step
                    if status:
                        workflow.status = status
                    db.commit()
                    
                    self.logger.info("Workflow step updated",
                                   workflow_id=str(workflow_id),
                                   step=step,
                                   status=status)
                else:
                    self.logger.warning("Workflow not found for update",
                                      workflow_id=str(workflow_id))
            except Exception as e:
                self.logger.error("Failed to update workflow step", error=str(e))
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            self.logger.error("Failed to create database session for workflow update", error=str(e))