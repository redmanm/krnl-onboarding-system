#!/usr/bin/env python3
"""
Test Audit API Endpoints
Tests the audit API endpoints directly to see if they return data
"""

import requests
import json
from datetime import datetime

def test_audit_endpoints():
    """Test all audit-related API endpoints"""
    print("🔍 Testing Audit API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test agent performance endpoints
    agents = ['validator', 'account_setup', 'scheduler', 'notifier']
    
    for agent in agents:
        print(f"\n🤖 Testing {agent} performance...")
        try:
            response = requests.get(f"{base_url}/api/v1/audit/agent-performance/{agent}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                print(f"   ✅ Success! Total executions: {metrics.get('total_executions', 0)}")
                print(f"      Success rate: {metrics.get('success_rate', 0):.1f}%")
                print(f"      Avg time: {metrics.get('average_execution_time_ms', 0):.0f}ms")
                if 'data_source' in data:
                    print(f"      Data source: {data['data_source']}")
                if 'error' in data:
                    print(f"      ⚠️  Error in response: {data['error']}")
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    # Test system health
    print(f"\n🏥 Testing system health...")
    try:
        response = requests.get(f"{base_url}/api/v1/audit/system-health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            workflow_metrics = data.get('workflow_metrics', {})
            agent_metrics = data.get('agent_metrics', {})
            
            print(f"   ✅ Success! System status: {data.get('system_status', 'unknown')}")
            print(f"      Total workflows: {workflow_metrics.get('total_workflows', 0)}")
            print(f"      Success rate: {workflow_metrics.get('success_rate', 0):.1f}%")
            print(f"      Active agents: {len(agent_metrics)}")
            if 'data_source' in data:
                print(f"      Data source: {data['data_source']}")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            print(f"      Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test log search
    print(f"\n🔍 Testing log search...")
    try:
        search_filters = {
            "limit": 10
        }
        
        response = requests.post(
            f"{base_url}/api/v1/audit/search-logs",
            json=search_filters,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            print(f"   ✅ Success! Found {len(logs)} logs")
            print(f"      Result count: {data.get('result_count', 0)}")
            if logs:
                print(f"      Latest log: {logs[0].get('agent_type', 'unknown')} - {logs[0].get('status', 'unknown')}")
            if 'data_source' in data:
                print(f"      Data source: {data['data_source']}")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            print(f"      Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def test_api_health():
    """Test basic API health"""
    print("🏥 Testing API Health")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and responding")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def check_recent_workflows():
    """Check if there are recent workflows that should have logs"""
    print("\n📊 Checking Recent Workflows")
    print("=" * 35)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/employees?limit=5", timeout=10)
        
        if response.status_code == 200:
            employees = response.json()
            print(f"✅ Found {len(employees)} employees")
            
            completed_workflows = [emp for emp in employees if emp.get('workflow_status') == 'completed']
            failed_workflows = [emp for emp in employees if emp.get('workflow_status') == 'failed']
            
            print(f"   Completed workflows: {len(completed_workflows)}")
            print(f"   Failed workflows: {len(failed_workflows)}")
            
            if completed_workflows:
                print("   Recent completed:")
                for emp in completed_workflows[:3]:
                    print(f"      - {emp.get('name', 'Unknown')}: {emp.get('workflow_status', 'unknown')}")
            
            return len(employees) > 0
        else:
            print(f"❌ Failed to get employees: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 AUDIT API DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test API health first
    api_healthy = test_api_health()
    
    if not api_healthy:
        print("\n❌ API is not responding. Make sure the backend is running.")
        exit(1)
    
    # Check workflows
    workflows_exist = check_recent_workflows()
    
    # Test audit endpoints
    test_audit_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if workflows_exist:
        print("✅ Workflows exist in the system")
        print("💡 If audit endpoints show 0 executions:")
        print("   1. Agent logs might not be written to database")
        print("   2. Database session issues in agents")
        print("   3. Audit service initialization problems")
    else:
        print("⚠️  No workflows found in system")
        print("💡 Create some employees first to generate agent logs")
    
    print("\n🔧 Troubleshooting:")
    print("   1. Check Docker logs: docker-compose logs backend")
    print("   2. Verify database connectivity")
    print("   3. Check agent execution logs in application output")