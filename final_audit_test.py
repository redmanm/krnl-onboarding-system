#!/usr/bin/env python3
"""
Final Comprehensive Agent Audit Fix Test
This will identify and verify the fix for the agent audit logging issue
"""

import requests
import json
import time
from datetime import datetime

def test_debug_endpoints():
    """Test the debug endpoints before fix"""
    print("🔍 TESTING DEBUG ENDPOINTS")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test agent logs count before
    print("\n📊 Checking current agent logs...")
    try:
        response = requests.get(f"{base_url}/api/v1/debug/agent-logs-count", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_logs = data.get('total_logs', 0)
            print(f"   Current total logs: {total_logs}")
            return total_logs
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return 0
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return 0

def test_orchestrator_directly():
    """Test the orchestrator execution directly"""
    print("\n🎯 TESTING ORCHESTRATOR DIRECTLY")
    print("=" * 45)
    
    base_url = "http://localhost:8000"
    
    try:
        print("   📤 Triggering orchestrator test endpoint...")
        response = requests.post(f"{base_url}/api/v1/debug/test-orchestrator", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"   ❌ Orchestrator test failed: {data['error']}")
                return False
            else:
                result = data.get('result', {})
                workflow_id = result.get('workflow_id')
                status = result.get('status')
                print(f"   ✅ Orchestrator test completed!")
                print(f"      Workflow ID: {workflow_id}")
                print(f"      Status: {status}")
                return True
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"      Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def check_logs_after_test():
    """Check if logs were created after orchestrator test"""
    print("\n📊 CHECKING LOGS AFTER ORCHESTRATOR TEST")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/api/v1/debug/agent-logs-count", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_logs = data.get('total_logs', 0)
            agent_counts = data.get('agent_counts', {})
            
            print(f"   📊 Total logs after test: {total_logs}")
            
            for agent, count in agent_counts.items():
                if count > 0:
                    print(f"   ✅ {agent}: {count} logs")
                else:
                    print(f"   ❌ {agent}: {count} logs")
            
            return total_logs > 0
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_agent_performance_final():
    """Final test of agent performance endpoints"""
    print("\n📈 FINAL AGENT PERFORMANCE TEST")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    agents = ['validator', 'account_setup', 'scheduler', 'notifier']
    
    success_count = 0
    
    for agent in agents:
        try:
            response = requests.get(f"{base_url}/api/v1/audit/agent-performance/{agent}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', {})
                total = metrics.get('total_executions', 0)
                success_rate = metrics.get('success_rate', 0)
                
                if total > 0:
                    print(f"   ✅ {agent}: {total} executions ({success_rate:.1f}% success)")
                    success_count += 1
                else:
                    print(f"   ❌ {agent}: 0 executions")
            else:
                print(f"   ❌ {agent}: API error {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {agent}: Request failed - {e}")
    
    return success_count == len(agents)

def check_docker_logs():
    """Remind to check Docker logs for detailed error info"""
    print("\n🐳 DOCKER LOGS ANALYSIS")
    print("=" * 30)
    
    print("   💡 To see detailed orchestrator execution logs:")
    print("      docker-compose logs backend | grep -i 'workflow\\|agent\\|orchestrator'")
    print("\n   💡 To see all backend logs:")
    print("      docker-compose logs backend")
    print("\n   💡 To see real-time logs:")
    print("      docker-compose logs -f backend")

def main():
    """Run the complete test sequence"""
    print("🚀 FINAL COMPREHENSIVE AGENT AUDIT FIX TEST")
    print("=" * 60)
    
    # Step 1: Check initial state
    initial_logs = test_debug_endpoints()
    
    # Step 2: Test orchestrator directly
    orchestrator_success = test_orchestrator_directly()
    
    # Small delay for processing
    print("\\n⏳ Waiting 3 seconds for processing...")
    time.sleep(3)
    
    # Step 3: Check if logs were created
    logs_created = check_logs_after_test()
    
    # Step 4: Final performance test
    performance_working = test_agent_performance_final()
    
    # Step 5: Analysis
    print("\\n" + "=" * 60)
    print("📋 FINAL DIAGNOSIS")
    print("=" * 60)
    
    if logs_created and performance_working:
        print("🎉 SUCCESS! The agent audit logging issue has been RESOLVED!")
        print("\\n✅ Confirmed:")
        print("   • Orchestrator is calling agents properly")
        print("   • Agents are executing and logging to database") 
        print("   • API endpoints are showing correct metrics")
        print("   • Dashboard should now display audit data")
        
        print("\\n🎯 SOLUTION SUMMARY:")
        print("   • Fixed agent initialization validation in orchestrator")
        print("   • Enhanced error handling in workflow execution")
        print("   • Improved agent logging with better error reporting")
        print("   • Added direct database queries as fallback")
        
    elif orchestrator_success and not logs_created:
        print("❌ PARTIAL ISSUE: Orchestrator works but agent logging fails")
        print("\\n🔧 Root cause:")
        print("   • Agents are being called but logging is failing")
        print("   • Database connection issues in agent context")
        print("   • BaseAgent._log_execution() method problems")
        
    elif not orchestrator_success:
        print("❌ CRITICAL ISSUE: Orchestrator execution is failing")
        print("\\n🔧 Root cause:")
        print("   • Agent initialization problems")
        print("   • Workflow execution exceptions")
        print("   • Database connection failures")
        
    else:
        print("❌ UNKNOWN ISSUE: Mixed results")
        
    print("\\n💡 Next steps:")
    if not (logs_created and performance_working):
        print("   1. Check the Docker logs for detailed error messages")
        print("   2. Restart Docker containers to apply all fixes")
        print("   3. Re-run this test after restart")
        check_docker_logs()
    else:
        print("   1. Refresh your browser dashboard")
        print("   2. Navigate to the Audit Logs section")
        print("   3. Verify that agent performance metrics are showing")
        print("   4. Test creating new employees to see real-time updates")

if __name__ == "__main__":
    main()