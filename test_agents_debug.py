#!/usr/bin/env python3
"""
Agent Debug Test Script
Diagnoses issues with the multi-agent onboarding system
"""

import asyncio
import sys
import os
import traceback
from datetime import datetime
import uuid

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test all required imports"""
    print("=== Testing Imports ===")
    
    try:
        import structlog
        print("✅ structlog imported successfully")
    except ImportError as e:
        print(f"❌ structlog import failed: {e}")
        return False
    
    try:
        from backend.database import get_db, create_tables
        print("✅ database module imported successfully")
    except ImportError as e:
        print(f"❌ database import failed: {e}")
        return False
    
    try:
        from backend.models import Employee, OnboardingWorkflow, AgentLog
        print("✅ models imported successfully")
    except ImportError as e:
        print(f"❌ models import failed: {e}")
        return False
    
    try:
        from backend.agents.base_agent import BaseAgent
        print("✅ BaseAgent imported successfully")
    except ImportError as e:
        print(f"❌ BaseAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.validator_agent import ValidatorAgent
        print("✅ ValidatorAgent imported successfully")
    except ImportError as e:
        print(f"❌ ValidatorAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.account_setup_agent import AccountSetupAgent
        print("✅ AccountSetupAgent imported successfully")
    except ImportError as e:
        print(f"❌ AccountSetupAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.scheduler_agent import SchedulerAgent
        print("✅ SchedulerAgent imported successfully")
    except ImportError as e:
        print(f"❌ SchedulerAgent import failed: {e}")
        return False
    
    try:
        from backend.agents.notifier_agent import NotifierAgent
        print("✅ NotifierAgent imported successfully")
    except ImportError as e:
        print(f"❌ NotifierAgent import failed: {e}")
        return False
    
    try:
        from backend.communication.a2a_system import A2ACommunicationBus
        print("✅ A2ACommunicationBus imported successfully")
    except ImportError as e:
        print(f"❌ A2ACommunicationBus import failed: {e}")
        print("  This might be due to Redis dependency issues")
        return False
    
    try:
        from backend.orchestrator import OnboardingOrchestrator
        print("✅ OnboardingOrchestrator imported successfully")
    except ImportError as e:
        print(f"❌ OnboardingOrchestrator import failed: {e}")
        return False
    
    return True

def test_agent_initialization():
    """Test agent initialization"""
    print("\n=== Testing Agent Initialization ===")
    
    try:
        from backend.agents.validator_agent import ValidatorAgent
        validator = ValidatorAgent()
        print("✅ ValidatorAgent initialized successfully")
    except Exception as e:
        print(f"❌ ValidatorAgent initialization failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from backend.agents.account_setup_agent import AccountSetupAgent
        account_setup = AccountSetupAgent()
        print("✅ AccountSetupAgent initialized successfully")
    except Exception as e:
        print(f"❌ AccountSetupAgent initialization failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from backend.agents.scheduler_agent import SchedulerAgent
        scheduler = SchedulerAgent()
        print("✅ SchedulerAgent initialized successfully")
    except Exception as e:
        print(f"❌ SchedulerAgent initialization failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from backend.agents.notifier_agent import NotifierAgent
        notifier = NotifierAgent()
        print("✅ NotifierAgent initialized successfully")
    except Exception as e:
        print(f"❌ NotifierAgent initialization failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n=== Testing Database Connection ===")
    
    try:
        from backend.database import get_db
        db = next(get_db())
        print("✅ Database connection successful")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n=== Testing Redis Connection ===")
    
    try:
        import redis
        client = redis.from_url("redis://localhost:6379")
        client.ping()
        print("✅ Redis connection successful (localhost:6379)")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed (localhost:6379): {e}")
        
        try:
            client = redis.from_url("redis://redis:6379")
            client.ping()
            print("✅ Redis connection successful (redis:6379)")
            return True
        except Exception as e2:
            print(f"❌ Redis connection failed (redis:6379): {e2}")
            return False

async def test_validator_agent():
    """Test ValidatorAgent processing"""
    print("\n=== Testing ValidatorAgent Processing ===")
    
    try:
        from backend.agents.validator_agent import ValidatorAgent
        
        validator = ValidatorAgent()
        
        test_data = {
            "employee_data": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "Software Engineer",
                "department": "Engineering",
                "start_date": "2024-01-15"
            }
        }
        
        result = await validator.process(test_data)
        
        if result.get("is_valid"):
            print("✅ ValidatorAgent processed data successfully")
            print(f"   Cleaned data: {result.get('cleaned_data')}")
            return True
        else:
            print(f"❌ ValidatorAgent validation failed: {result.get('errors')}")
            return False
            
    except Exception as e:
        print(f"❌ ValidatorAgent processing failed: {e}")
        traceback.print_exc()
        return False

async def test_account_setup_agent():
    """Test AccountSetupAgent processing"""
    print("\n=== Testing AccountSetupAgent Processing ===")
    
    try:
        from backend.agents.account_setup_agent import AccountSetupAgent
        
        account_agent = AccountSetupAgent()
        
        test_data = {
            "employee_data": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "Software Engineer",
                "department": "Engineering",
                "start_date": "2024-01-15"
            },
            "employee_id": uuid.uuid4()
        }
        
        result = await account_agent.process(test_data)
        
        if result.get("account_created"):
            print("✅ AccountSetupAgent processed data successfully")
            print(f"   Username: {result.get('username')}")
            return True
        else:
            print(f"❌ AccountSetupAgent processing failed")
            return False
            
    except Exception as e:
        print(f"❌ AccountSetupAgent processing failed: {e}")
        traceback.print_exc()
        return False

async def test_orchestrator():
    """Test OnboardingOrchestrator"""
    print("\n=== Testing OnboardingOrchestrator ===")
    
    try:
        from backend.orchestrator import OnboardingOrchestrator
        
        # Initialize without Redis for testing
        orchestrator = OnboardingOrchestrator(redis_url=None)
        print("✅ OnboardingOrchestrator initialized successfully")
        
        test_employee_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "start_date": "2024-01-15"
        }
        
        print("🔄 Starting test workflow...")
        result = await orchestrator.start_onboarding_workflow(test_employee_data)
        
        if result.get("status") == "completed":
            print("✅ OnboardingOrchestrator workflow completed successfully")
            print(f"   Workflow ID: {result.get('workflow_id')}")
            return True
        else:
            print(f"❌ OnboardingOrchestrator workflow failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ OnboardingOrchestrator test failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all diagnostic tests"""
    print("🔍 KRNL Agent System Diagnostic Tool")
    print("=" * 50)
    
    results = []
    
    # Test imports
    results.append(test_imports())
    
    # Test agent initialization
    results.append(test_agent_initialization())
    
    # Test database connection
    results.append(test_database_connection())
    
    # Test Redis connection
    results.append(test_redis_connection())
    
    # Test individual agents
    results.append(await test_validator_agent())
    results.append(await test_account_setup_agent())
    
    # Test orchestrator
    results.append(await test_orchestrator())
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Agent system should be working.")
    else:
        print("❌ Some tests failed. Check the errors above for details.")
        print("\nCommon issues and solutions:")
        print("- Database connection: Ensure PostgreSQL is running")
        print("- Redis connection: Ensure Redis is running")
        print("- Import errors: Check dependencies in requirements.txt")
        print("- Agent initialization: Check for missing configurations")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())