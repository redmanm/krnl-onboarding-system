#!/usr/bin/env python3
"""
Comprehensive Audit Debug Test
Identifies the exact issue with audit logs not showing in dashboard
"""

import requests
import json
from datetime import datetime

def test_debug_endpoints():
    """Test the new debug endpoints"""
    print("🔍 Testing Debug Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test agent logs count
    print("\n📊 Checking agent logs count...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/agent-logs-count", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_logs = data.get('total_logs', 0)
            agent_counts = data.get('agent_counts', {})
            
            print(f"   ✅ Total agent logs in database: {total_logs}")
            
            for agent, count in agent_counts.items():
                print(f"   🤖 {agent}: {count} logs")
            
            if total_logs == 0:
                print("   ⚠️  No agent logs found! This is the root issue.")
                return False
            else:
                print("   ✅ Agent logs exist in database!")
                return True
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def create_test_log():
    """Create a test log to verify logging works"""
    print("\n🧪 Creating test agent log...")
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/debug/create-test-log?agent_type=test_validator",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"   ⚠️  {data['error']}")
                return False
            else:
                print(f"   ✅ Test log created: {data.get('log_id')}")
                return True
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            print(f"      Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_agent_performance_after_log():
    """Test agent performance after creating test log"""
    print("\n📈 Testing agent performance after creating test log...")
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/api/v1/audit/agent-performance/test_validator", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {})
            total_executions = metrics.get('total_executions', 0)
            
            print(f"   ✅ API Response received")
            print(f"      Total executions: {total_executions}")
            print(f"      Success rate: {metrics.get('success_rate', 0):.1f}%")
            print(f"      Data source: {data.get('data_source', 'unknown')}")
            
            if total_executions > 0:
                print("   ✅ Agent performance data is working!")
                return True
            else:
                print("   ❌ Still showing 0 executions")
                return False
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_real_workflow():
    """Create a real workflow and check if it generates logs"""
    print("\n🔄 Testing real workflow...")
    
    base_url = "http://localhost:8000"
    
    # Create an employee to trigger a real workflow
    employee_data = {\n        \"name\": \"Debug Test User\",\n        \"email\": \"debug.test@krnl.com\",\n        \"role\": \"Software Engineer\",\n        \"department\": \"Engineering\",\n        \"start_date\": \"2024-02-01\"\n    }\n    \n    try:\n        print(\"   📤 Creating employee to trigger workflow...\")\n        response = requests.post(\n            f\"{base_url}/api/v1/employees\",\n            json=employee_data,\n            headers={\"Content-Type\": \"application/json\"},\n            timeout=30\n        )\n        \n        if response.status_code == 200:\n            result = response.json()\n            workflow_id = result.get('workflow_id')\n            print(f\"   ✅ Employee created, workflow: {workflow_id}\")\n            \n            # Wait a moment for agents to process\n            import time\n            print(\"   ⏳ Waiting 2 seconds for agents to process...\")\n            time.sleep(2)\n            \n            return True\n        else:\n            print(f\"   ❌ Failed to create employee: {response.status_code}\")\n            return False\n            \n    except Exception as e:\n        print(f\"   ❌ Request failed: {e}\")\n        return False

def final_check():
    \"\"\"Final check of all agent performance\"\"\"\n    print(\"\\n🏁 Final Agent Performance Check\")\n    print(\"=\" * 40)\n    \n    base_url = \"http://localhost:8000\"\n    agents = ['validator', 'account_setup', 'scheduler', 'notifier']\n    \n    all_good = True\n    \n    for agent in agents:\n        try:\n            response = requests.get(f\"{base_url}/api/v1/audit/agent-performance/{agent}\", timeout=10)\n            \n            if response.status_code == 200:\n                data = response.json()\n                metrics = data.get('metrics', {})\n                total = metrics.get('total_executions', 0)\n                success_rate = metrics.get('success_rate', 0)\n                \n                if total > 0:\n                    print(f\"   ✅ {agent}: {total} executions ({success_rate:.1f}% success)\")\n                else:\n                    print(f\"   ❌ {agent}: 0 executions\")\n                    all_good = False\n            else:\n                print(f\"   ❌ {agent}: API error {response.status_code}\")\n                all_good = False\n                \n        except Exception as e:\n            print(f\"   ❌ {agent}: Request failed - {e}\")\n            all_good = False\n    \n    return all_good

if __name__ == \"__main__\":\n    print(\"🔍 COMPREHENSIVE AUDIT DEBUG TEST\")\n    print(\"=\" * 60)\n    \n    # Step 1: Check if logs exist\n    logs_exist = test_debug_endpoints()\n    \n    if not logs_exist:\n        print(\"\\n🔧 No logs found. Testing log creation...\")\n        \n        # Step 2: Try to create a test log\n        test_log_created = create_test_log()\n        \n        if test_log_created:\n            # Step 3: Test if performance endpoint works with test log\n            test_agent_performance_after_log()\n        \n        # Step 4: Create a real workflow\n        test_real_workflow()\n        \n        # Step 5: Check logs count again\n        print(\"\\n📊 Rechecking agent logs after tests...\")\n        test_debug_endpoints()\n    \n    # Final check\n    all_working = final_check()\n    \n    print(\"\\n\" + \"=\" * 60)\n    print(\"📋 DIAGNOSIS SUMMARY\")\n    print(\"=\" * 60)\n    \n    if all_working:\n        print(\"✅ ISSUE RESOLVED: Agent performance data is now showing!\")\n        print(\"\\n🎉 The audit logs should now be visible in the dashboard.\")\n    else:\n        print(\"❌ ISSUE PERSISTS: Audit logs still not working properly.\")\n        print(\"\\n🔧 Possible causes:\")\n        print(\"   1. Agents are not actually executing their process() methods\")\n        print(\"   2. Database logging is failing silently in agent execution\")\n        print(\"   3. Agent logging is bypassed during heartbeat-only operation\")\n        print(\"   4. Database connection issues in agent contexts\")\n        \n        print(\"\\n💡 Next steps:\")\n        print(\"   1. Check Docker logs: docker-compose logs backend\")\n        print(\"   2. Look for agent execution logs in application output\")\n        print(\"   3. Verify agents are processing workflows, not just heartbeats\")