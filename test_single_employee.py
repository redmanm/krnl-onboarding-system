#!/usr/bin/env python3
"""
Simple test to create a single employee via API and check the result
"""

import requests
import json
import time

# Test data
test_employee = {
    "name": "Test User",
    "email": "test.user@company.com", 
    "role": "Software Engineer",
    "department": "Engineering",
    "start_date": "2025-09-01"
}

def test_single_employee():
    """Test creating a single employee and check workflow status"""
    
    print("🧪 Testing Single Employee Workflow")
    print("=" * 50)
    
    # Test 1: Create employee
    print("1. Creating employee...")
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/employees",
            json=test_employee,
            timeout=60  # Increased timeout for workflow processing
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Employee created successfully")
        print(f"   Workflow ID: {result['workflow_id']}")
        print(f"   Employee ID: {result['employee_id']}")
        print(f"   Status: {result['status']}")
        
        workflow_id = result['workflow_id']
        
    except Exception as e:
        print(f"❌ Failed to create employee: {e}")
        return False
    
    # Test 2: Wait and check workflow status
    print("\n2. Checking workflow status...")
    time.sleep(5)  # Wait for workflow to complete
    
    try:
        response = requests.get(
            f"http://localhost:8000/api/v1/workflows/{workflow_id}",
            timeout=10
        )
        response.raise_for_status()
        workflow_status = response.json()
        
        print(f"   Workflow Status: {workflow_status['status']}")
        print(f"   Current Step: {workflow_status['current_step']}")
        print(f"   Logs Count: {len(workflow_status.get('logs', []))}")
        
        # Print detailed logs
        if workflow_status.get('logs'):
            print("\n3. Workflow Execution Logs:")
            for i, log in enumerate(workflow_status['logs'], 1):
                status_icon = "✅" if log['status'] == 'success' else "❌"
                print(f"   {i}. {status_icon} {log['agent_type']}: {log['action']} ({log['status']}) - {log['execution_time_ms']}ms")
        
        # Check if workflow completed successfully
        if workflow_status['status'] == 'completed':
            print("\n🎉 Workflow completed successfully!")
            return True
        elif workflow_status['status'] == 'failed':
            print(f"\n❌ Workflow failed at step: {workflow_status['current_step']}")
            return False
        else:
            print(f"\n⏳ Workflow still in progress: {workflow_status['status']}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to get workflow status: {e}")
        return False

def test_dashboard_stats():
    """Test dashboard stats to see overall system status"""
    print("\n4. Checking dashboard stats...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/dashboard/stats")
        response.raise_for_status()
        stats = response.json()
        
        print(f"   Total Employees: {stats['total_employees']}")
        print(f"   Pending: {stats['pending_onboarding']}")
        print(f"   Completed: {stats['completed_onboarding']}")
        print(f"   Failed: {stats['failed_onboarding']}")
        print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
        
    except Exception as e:
        print(f"❌ Failed to get dashboard stats: {e}")

if __name__ == "__main__":
    # First check if API is accessible
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        print("✅ API is accessible")
    except Exception as e:
        print(f"❌ Cannot access API: {e}")
        print("Make sure the backend service is running: docker-compose ps")
        exit(1)
    
    # Run the test
    success = test_single_employee()
    test_dashboard_stats()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Single employee workflow test PASSED!")
        print("The workflow system is working correctly.")
    else:
        print("❌ Single employee workflow test FAILED!")
        print("Check the logs above for specific issues.")