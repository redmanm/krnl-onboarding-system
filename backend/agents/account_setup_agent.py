import random
import string
from typing import Dict, Any, List
from database import get_db
from models import SystemAccount, Employee
from .base_agent import BaseAgent
import uuid

try:
    from communication.a2a_system import A2AAgent, A2ACommunicationBus
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    A2AAgent = object  # Fallback base class
    A2ACommunicationBus = None

class AccountSetupAgent(BaseAgent):
    """Agent responsible for setting up system accounts and permissions"""
    
    def __init__(self, communication_bus=None):
        BaseAgent.__init__(self, "account_setup")
        
        # Initialize A2A capabilities if available
        if A2A_AVAILABLE and communication_bus:
            try:
                A2AAgent.__init__(self, "account_setup", communication_bus)
                self.communication_bus = communication_bus
            except Exception as e:
                self.logger.warning(f"Failed to initialize A2A capabilities: {e}")
                self.communication_bus = None
        else:
            self.communication_bus = None
        self.role_permissions = {
            "Software Engineer": [
                "read_code_repository",
                "write_code_repository", 
                "access_development_tools",
                "access_staging_environment",
                "view_project_documentation"
            ],
            "Product Manager": [
                "manage_product_backlog",
                "access_analytics_dashboard",
                "view_user_feedback",
                "manage_feature_flags",
                "access_project_reports"
            ],
            "Designer": [
                "access_design_tools",
                "manage_design_assets",
                "view_user_research",
                "access_prototype_tools",
                "collaborate_on_designs"
            ],
            "QA Engineer": [
                "access_testing_tools",
                "view_test_results",
                "manage_test_cases",
                "access_bug_tracking",
                "access_staging_environment"
            ],
            "DevOps Engineer": [
                "manage_infrastructure",
                "access_monitoring_tools",
                "manage_deployments",
                "access_production_environment",
                "manage_ci_cd_pipelines"
            ],
            "Data Scientist": [
                "access_data_warehouse",
                "use_analytics_tools",
                "manage_ml_models",
                "access_compute_resources",
                "view_data_reports"
            ],
            "Marketing Manager": [
                "manage_campaigns",
                "access_marketing_tools",
                "view_customer_data",
                "manage_content",
                "access_social_media"
            ],
            "Sales Representative": [
                "access_crm_system",
                "view_customer_contacts",
                "manage_sales_pipeline",
                "access_sales_reports",
                "use_communication_tools"
            ],
            "HR Specialist": [
                "manage_employee_data",
                "access_hr_systems",
                "view_personnel_records",
                "manage_benefits",
                "access_payroll_system"
            ],
            "Finance Analyst": [
                "access_financial_data",
                "manage_budgets",
                "view_expense_reports",
                "access_accounting_system",
                "generate_financial_reports"
            ]
        }
        
        self.base_permissions = [
            "access_company_directory",
            "use_email_system",
            "access_employee_handbook",
            "use_collaboration_tools",
            "access_time_tracking"
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create system account with role-based permissions"""
        employee_data = input_data.get("employee_data", {})
        employee_id = input_data.get("employee_id")
        
        if not employee_id:
            raise ValueError("employee_id is required")
        
        # Generate username
        username = self._generate_username(
            employee_data.get("name", ""), 
            employee_data.get("email", "")
        )
        
        # Get role-based permissions
        role = employee_data.get("role", "")
        permissions = self._get_permissions_for_role(role)
        
        # Create account in database
        account_data = await self._create_system_account(
            employee_id, username, permissions
        )
        
        # A2A Communication: Notify Scheduler Agent about account creation
        if A2A_AVAILABLE and hasattr(self, 'communication_bus') and self.communication_bus:
            try:
                scheduler_response = await self.call_agent(
                    target_agent="scheduler",
                    method="account_created_notification",
                    params={
                        "employee_id": str(employee_id),
                        "employee_data": employee_data,
                        "account_data": {
                            "username": username,
                            "permissions": permissions
                        }
                    }
                )
                self.logger.info("Notified scheduler agent via A2A", 
                               response=scheduler_response)
            except Exception as e:
                self.logger.warning("Failed to notify scheduler agent", error=str(e))
        else:
            self.logger.debug("A2A communication not available or not configured")
        
        result = {
            "account_created": True,
            "username": username,
            "permissions": permissions,
            "account_details": {
                "employee_id": str(employee_id),
                "username": username,
                "role": role,
                "permission_count": len(permissions),
                "status": "active"
            },
            "next_steps": [
                "Password will be sent via secure channel",
                "Access will be activated on start date",
                "Training materials will be provided"
            ]
        }
        
        return result
    
    def _generate_username(self, name: str, email: str) -> str:
        """Generate a unique username based on name and email"""
        # Try firstname.lastname format first
        if name:
            parts = name.lower().split()
            if len(parts) >= 2:
                base_username = f"{parts[0]}.{parts[-1]}"
            else:
                base_username = parts[0] if parts else "user"
        else:
            # Fall back to email prefix
            base_username = email.split("@")[0] if email else "user"
        
        # Remove special characters and ensure it's valid
        base_username = "".join(c for c in base_username if c.isalnum() or c in "._-")
        
        # Ensure uniqueness by checking database
        username = base_username
        counter = 1
        
        while self._username_exists(username):
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    def _username_exists(self, username: str) -> bool:
        """Check if username already exists in database"""
        try:
            db = next(get_db())
            try:
                existing = db.query(SystemAccount).filter(
                    SystemAccount.username == username
                ).first()
                return existing is not None
            except Exception as e:
                self.logger.warning(f"Error querying username: {e}")
                return False
            finally:
                db.close()
        except Exception as e:
            self.logger.warning(f"Error creating database session for username check: {e}")
            return False
    
    def _get_permissions_for_role(self, role: str) -> List[str]:
        """Get permissions based on employee role"""
        role_perms = self.role_permissions.get(role, [])
        all_permissions = self.base_permissions + role_perms
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(all_permissions))
    
    async def _create_system_account(self, employee_id: uuid.UUID, 
                                   username: str, permissions: List[str]) -> Dict[str, Any]:
        """Create system account in database"""
        try:
            db = next(get_db())
            try:
                # Verify employee exists
                employee = db.query(Employee).filter(Employee.id == employee_id).first()
                if not employee:
                    raise ValueError(f"Employee with ID {employee_id} not found")
                
                # Create system account
                account = SystemAccount(
                    employee_id=employee_id,
                    username=username,
                    permissions=permissions,
                    status="active"
                )
                
                db.add(account)
                db.commit()
                db.refresh(account)
                
                self.logger.info("System account created successfully",
                               username=username,
                               employee_id=str(employee_id))
                
                return {
                    "id": str(account.id),
                    "employee_id": str(account.employee_id),
                    "username": account.username,
                    "permissions": account.permissions,
                    "status": account.status,
                    "created_at": account.created_at.isoformat()
                }
            except Exception as e:
                self.logger.error(f"Failed to create system account in database: {e}")
                db.rollback()
                raise
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"Failed to create database session for account creation: {e}")
            raise
    
    def _generate_temp_password(self) -> str:
        """Generate a temporary password (in real system, this would be more secure)"""
        length = 12
        characters = string.ascii_letters + string.digits + "!@#$%"
        return "".join(random.choice(characters) for _ in range(length))