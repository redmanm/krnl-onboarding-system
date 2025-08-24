#!/usr/bin/env python3
"""
KRNL Onboarding System - Workflow Test Script
This script helps test individual workflow components to identify issues.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agents.validator_agent import ValidatorAgent
from agents.account_setup_agent import AccountSetupAgent
from agents.scheduler_agent import SchedulerAgent
from agents.notifier_agent import NotifierAgent
import uuid
from datetime import datetime

async def test_validator_agent():
    """Test the validator agent independently"""
    print("Testing Validator Agent...")
    
    validator = ValidatorAgent()
    
    # Test data
    test_data = {
        "employee_data": {
            "name": "John Doe",
            "email": "john.doe@company.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "start_date": "2025-09-01"
        }
    }
    
    try:
        result = await validator.process(test_data)
        print("✅ Validator Agent Test PASSED")
        print(f"   Validation Result: {result['is_valid']}")
        print(f"   Errors: {len(result['errors'])}")
        print(f"   Warnings: {len(result['warnings'])}")
        return True
    except Exception as e:
        print(f"❌ Validator Agent Test FAILED: {e}")
        return False

async def test_account_setup_agent():
    """Test the account setup agent independently"""
    print("\nTesting Account Setup Agent...")
    
    account_agent = AccountSetupAgent(communication_bus=None)  # No communication bus for testing
    
    # Test data
    test_data = {
        "employee_data": {
            "name": "John Doe",
            "email": "john.doe@company.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "start_date": "2025-09-01"
        },
        "employee_id": uuid.uuid4()
    }
    
    try:
        result = await account_agent.process(test_data)
        print("✅ Account Setup Agent Test PASSED")
        print(f"   Account Created: {result['account_created']}")
        print(f"   Username: {result['username']}")
        print(f"   Permissions Count: {len(result['permissions'])}")
        return True
    except Exception as e:
        print(f"❌ Account Setup Agent Test FAILED: {e}")
        return False

async def test_scheduler_agent():
    """Test the scheduler agent independently"""
    print("\nTesting Scheduler Agent...")
    
    scheduler = SchedulerAgent()
    
    # Test data
    test_data = {
        "employee_data": {
            "name": "John Doe",
            "email": "john.doe@company.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "start_date": "2025-09-01"
        },
        "employee_id": uuid.uuid4()
    }
    
    try:
        result = await scheduler.process(test_data)
        print("✅ Scheduler Agent Test PASSED")
        print(f"   Events Scheduled: {len(result.get('scheduled_events', []))}")
        return True
    except Exception as e:
        print(f"❌ Scheduler Agent Test FAILED: {e}")
        return False

async def test_notifier_agent():
    """Test the notifier agent independently"""
    print("\nTesting Notifier Agent...")
    
    notifier = NotifierAgent()
    
    # Test data
    test_data = {
        "employee_data": {
            "name": "John Doe",
            "email": "john.doe@company.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "start_date": "2025-09-01"
        },
        "employee_id": uuid.uuid4()
    }
    
    try:
        result = await notifier.process(test_data)
        print("✅ Notifier Agent Test PASSED")
        print(f"   Notifications Sent: {len(result.get('notifications_sent', []))}")
        return True
    except Exception as e:
        print(f"❌ Notifier Agent Test FAILED: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 KRNL Onboarding System - Workflow Component Tests")
    print("=" * 60)
    
    tests = [
        test_validator_agent,
        test_account_setup_agent,
        test_scheduler_agent,
        test_notifier_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All workflow components are working correctly!")
        print("   The issue might be in the orchestrator or database connection.")
    else:
        print("⚠️  Some workflow components are failing.")
        print("   Check the error messages above for specific issues.")
    
    print("\n💡 Next Steps:")
    print("   1. Fix any failing components")
    print("   2. Restart the backend service: docker-compose restart backend")
    print("   3. Check backend logs: docker-compose logs backend")
    print("   4. Test the upload functionality again")

if __name__ == "__main__":
    asyncio.run(main())