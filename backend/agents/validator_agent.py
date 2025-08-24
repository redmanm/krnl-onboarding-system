import re
from typing import Dict, Any, List
from datetime import datetime, date
from .base_agent import BaseAgent

class ValidatorAgent(BaseAgent):
    """Agent responsible for validating and cleaning employee data"""
    
    def __init__(self):
        super().__init__("validator")
        self.required_fields = ["name", "email", "role", "department", "start_date"]
        self.valid_roles = [
            "Software Engineer", "Product Manager", "Designer", "QA Engineer",
            "DevOps Engineer", "Data Scientist", "Marketing Manager", 
            "Sales Representative", "HR Specialist", "Finance Analyst"
        ]
        self.valid_departments = [
            "Engineering", "Product", "Design", "QA", "DevOps", 
            "Data Science", "Marketing", "Sales", "HR", "Finance"
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean employee data"""
        employee_data = input_data.get("employee_data", {})
        
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "cleaned_data": {},
            "validation_summary": {}
        }
        
        # Check required fields
        for field in self.required_fields:
            if field not in employee_data or not employee_data[field]:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["is_valid"] = False
        
        if not validation_results["is_valid"]:
            return validation_results
        
        # Clean and validate each field
        cleaned_data = {}
        
        # Name validation and cleaning
        name = self._clean_name(employee_data["name"])
        if len(name) < 2:
            validation_results["errors"].append("Name must be at least 2 characters long")
            validation_results["is_valid"] = False
        else:
            cleaned_data["name"] = name
        
        # Email validation
        email = self._clean_email(employee_data["email"])
        if not self._is_valid_email(email):
            validation_results["errors"].append("Invalid email format")
            validation_results["is_valid"] = False
        else:
            cleaned_data["email"] = email
        
        # Role validation
        role = self._clean_role(employee_data["role"])
        if role not in self.valid_roles:
            validation_results["warnings"].append(f"Unusual role: {role}. Consider using standard roles.")
        cleaned_data["role"] = role
        
        # Department validation
        department = self._clean_department(employee_data["department"])
        if department not in self.valid_departments:
            validation_results["warnings"].append(f"Unusual department: {department}. Consider using standard departments.")
        cleaned_data["department"] = department
        
        # Start date validation
        try:
            start_date = self._parse_date(employee_data["start_date"])
            if start_date < date.today():
                validation_results["warnings"].append("Start date is in the past")
            cleaned_data["start_date"] = start_date.isoformat()
        except ValueError as e:
            validation_results["errors"].append(f"Invalid start date: {str(e)}")
            validation_results["is_valid"] = False
        
        validation_results["cleaned_data"] = cleaned_data
        validation_results["validation_summary"] = {
            "total_fields": len(self.required_fields),
            "valid_fields": len(cleaned_data),
            "error_count": len(validation_results["errors"]),
            "warning_count": len(validation_results["warnings"])
        }
        
        return validation_results
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize name"""
        # Remove extra whitespace and title case
        return " ".join(word.strip().title() for word in str(name).split() if word.strip())
    
    def _clean_email(self, email: str) -> str:
        """Clean email address"""
        return str(email).strip().lower()
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _clean_role(self, role: str) -> str:
        """Clean and normalize role"""
        # Title case and remove extra whitespace
        cleaned = " ".join(word.strip().title() for word in str(role).split() if word.strip())
        
        # Try to match with standard roles (fuzzy matching)
        for standard_role in self.valid_roles:
            if self._similarity_ratio(cleaned.lower(), standard_role.lower()) > 0.8:
                return standard_role
        
        return cleaned
    
    def _clean_department(self, department: str) -> str:
        """Clean and normalize department"""
        cleaned = " ".join(word.strip().title() for word in str(department).split() if word.strip())
        
        # Try to match with standard departments
        for standard_dept in self.valid_departments:
            if self._similarity_ratio(cleaned.lower(), standard_dept.lower()) > 0.8:
                return standard_dept
        
        return cleaned
    
    def _parse_date(self, date_str: Any) -> date:
        """Parse date from various formats"""
        if isinstance(date_str, date):
            return date_str
        
        date_str = str(date_str).strip()
        
        # Try different date formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%d-%m-%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _similarity_ratio(self, a: str, b: str) -> float:
        """Calculate simple similarity ratio between two strings"""
        # Simple Jaccard similarity
        set_a = set(a.split())
        set_b = set(b.split())
        
        if not set_a and not set_b:
            return 1.0
        
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        
        return intersection / union if union > 0 else 0.0