import pytest
import asyncio
from datetime import date, datetime
from unittest.mock import Mock, patch
import uuid

# Import the agent to test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.validator_agent import ValidatorAgent

class TestValidatorAgent:
    """Test suite for the Validator Agent"""
    
    @pytest.fixture
    def validator_agent(self):
        """Create a ValidatorAgent instance for testing"""
        return ValidatorAgent()
    
    @pytest.fixture
    def valid_employee_data(self):
        """Valid employee data for testing"""
        return {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "start_date": "2024-12-01"
        }
    
    @pytest.mark.asyncio
    async def test_valid_employee_data(self, validator_agent, valid_employee_data):
        """Test validation of valid employee data"""
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["cleaned_data"]["name"] == "John Doe"
        assert result["cleaned_data"]["email"] == "john.doe@example.com"
        assert result["validation_summary"]["total_fields"] == 5
        assert result["validation_summary"]["valid_fields"] == 5
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, validator_agent):
        """Test validation with missing required fields"""
        input_data = {
            "employee_data": {
                "name": "John Doe",
                "email": "john.doe@example.com"
                # Missing role, department, start_date
            }
        }
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) == 3
        assert "Missing required field: role" in result["errors"]
        assert "Missing required field: department" in result["errors"]
        assert "Missing required field: start_date" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_invalid_email_format(self, validator_agent, valid_employee_data):
        """Test validation with invalid email format"""
        valid_employee_data["email"] = "invalid-email"
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is False
        assert "Invalid email format" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_short_name(self, validator_agent, valid_employee_data):
        """Test validation with very short name"""
        valid_employee_data["name"] = "J"
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is False
        assert "Name must be at least 2 characters long" in result["errors"]
    
    @pytest.mark.asyncio
    async def test_name_cleaning(self, validator_agent, valid_employee_data):
        """Test name cleaning functionality"""
        valid_employee_data["name"] = "  john   doe  "
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert result["cleaned_data"]["name"] == "John Doe"
    
    @pytest.mark.asyncio
    async def test_email_cleaning(self, validator_agent, valid_employee_data):
        """Test email cleaning functionality"""
        valid_employee_data["email"] = "  JOHN.DOE@EXAMPLE.COM  "
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert result["cleaned_data"]["email"] == "john.doe@example.com"
    
    @pytest.mark.asyncio
    async def test_role_standardization(self, validator_agent, valid_employee_data):
        """Test role standardization"""
        valid_employee_data["role"] = "software engineer"  # lowercase
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert result["cleaned_data"]["role"] == "Software Engineer"
    
    @pytest.mark.asyncio
    async def test_department_standardization(self, validator_agent, valid_employee_data):
        """Test department standardization"""
        valid_employee_data["department"] = "engineering"  # lowercase
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert result["cleaned_data"]["department"] == "Engineering"
    
    @pytest.mark.asyncio
    async def test_unusual_role_warning(self, validator_agent, valid_employee_data):
        """Test warning for unusual role"""
        valid_employee_data["role"] = "Unicorn Specialist"
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0
        assert any("Unusual role" in warning for warning in result["warnings"])
    
    @pytest.mark.asyncio
    async def test_unusual_department_warning(self, validator_agent, valid_employee_data):
        """Test warning for unusual department"""
        valid_employee_data["department"] = "Magic Department"
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0
        assert any("Unusual department" in warning for warning in result["warnings"])
    
    @pytest.mark.asyncio
    async def test_past_start_date_warning(self, validator_agent, valid_employee_data):
        """Test warning for past start date"""
        valid_employee_data["start_date"] = "2023-01-01"
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True
        assert len(result["warnings"]) > 0
        assert any("Start date is in the past" in warning for warning in result["warnings"])
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(self, validator_agent, valid_employee_data):
        """Test validation with invalid date format"""
        valid_employee_data["start_date"] = "invalid-date"
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is False
        assert any("Invalid start date" in error for error in result["errors"])
    
    @pytest.mark.asyncio
    async def test_multiple_date_formats(self, validator_agent, valid_employee_data):
        """Test different date formats are parsed correctly"""
        date_formats = [
            "2024-12-01",      # ISO format
            "12/01/2024",      # US format
            "01/12/2024",      # EU format (day/month/year)
            "2024/12/01",      # Alternative ISO
            "12-01-2024",      # US with dashes
            "01-12-2024"       # EU with dashes
        ]
        
        for date_format in date_formats:
            valid_employee_data["start_date"] = date_format
            input_data = {"employee_data": valid_employee_data.copy()}
            
            result = await validator_agent.process(input_data)
            
            # Should either be valid or give a specific date parsing error
            if not result["is_valid"]:
                assert any("Invalid start date" in error for error in result["errors"])
            else:
                assert "start_date" in result["cleaned_data"]
    
    @pytest.mark.asyncio
    async def test_validation_summary(self, validator_agent, valid_employee_data):
        """Test validation summary is correctly generated"""
        input_data = {"employee_data": valid_employee_data}
        
        result = await validator_agent.process(input_data)
        
        summary = result["validation_summary"]
        assert summary["total_fields"] == 5
        assert summary["valid_fields"] == 5
        assert summary["error_count"] == 0
        assert summary["warning_count"] >= 0  # Could have warnings for past dates etc.
    
    def test_clean_name_edge_cases(self, validator_agent):
        """Test name cleaning edge cases"""
        # Test multiple spaces
        assert validator_agent._clean_name("  john    doe  ") == "John Doe"
        
        # Test single name
        assert validator_agent._clean_name("john") == "John"
        
        # Test empty string
        assert validator_agent._clean_name("") == ""
        
        # Test names with special characters
        assert validator_agent._clean_name("john o'connor") == "John O'Connor"
    
    def test_email_validation_edge_cases(self, validator_agent):
        """Test email validation edge cases"""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "123@example.org"
        ]
        
        for email in valid_emails:
            assert validator_agent._is_valid_email(email) is True
        
        # Invalid emails
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user space@example.com",
            "user..double.dot@example.com"
        ]
        
        for email in invalid_emails:
            assert validator_agent._is_valid_email(email) is False
    
    def test_similarity_ratio(self, validator_agent):
        """Test string similarity calculation"""
        # Identical strings
        assert validator_agent._similarity_ratio("test", "test") == 1.0
        
        # Completely different strings
        assert validator_agent._similarity_ratio("abc", "xyz") == 0.0
        
        # Partial similarity
        ratio = validator_agent._similarity_ratio("software engineer", "Software Engineer")
        assert ratio > 0.5  # Should have some similarity due to word overlap
        
        # Empty strings
        assert validator_agent._similarity_ratio("", "") == 1.0
    
    def test_parse_date_edge_cases(self, validator_agent):
        """Test date parsing edge cases"""
        # Already a date object
        test_date = date(2024, 12, 1)
        assert validator_agent._parse_date(test_date) == test_date
        
        # Valid date strings
        assert validator_agent._parse_date("2024-12-01") == date(2024, 12, 1)
        
        # Invalid date strings should raise ValueError
        with pytest.raises(ValueError):
            validator_agent._parse_date("invalid-date")
        
        with pytest.raises(ValueError):
            validator_agent._parse_date("2024-13-01")  # Invalid month
    
    @pytest.mark.asyncio
    async def test_comprehensive_validation_scenario(self, validator_agent):
        """Test a comprehensive validation scenario with multiple issues"""
        input_data = {
            "employee_data": {
                "name": "  jane   smith  ",  # Needs cleaning
                "email": "  JANE.SMITH@EXAMPLE.COM  ",  # Needs cleaning
                "role": "unicorn specialist",  # Unusual role
                "department": "magic",  # Unusual department
                "start_date": "2023-01-01"  # Past date
            }
        }
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is True  # Should still be valid despite warnings
        assert result["cleaned_data"]["name"] == "Jane Smith"
        assert result["cleaned_data"]["email"] == "jane.smith@example.com"
        assert len(result["warnings"]) >= 3  # Unusual role, department, past date
        assert result["validation_summary"]["error_count"] == 0
        assert result["validation_summary"]["warning_count"] >= 3
    
    @pytest.mark.asyncio
    async def test_empty_employee_data(self, validator_agent):
        """Test validation with empty employee data"""
        input_data = {"employee_data": {}}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) == 5  # All required fields missing
    
    @pytest.mark.asyncio
    async def test_none_employee_data(self, validator_agent):
        """Test validation with None employee data"""
        input_data = {}
        
        result = await validator_agent.process(input_data)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) == 5  # All required fields missing

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])