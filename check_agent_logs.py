#!/usr/bin/env python3
"""
Check Agent Logs in Database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import get_db
from backend.models import AgentLog, OnboardingWorkflow, Employee

def check_agent_logs():
    """Check if agent logs exist in database"""
    print("🔍 Checking Agent Logs in Database")
    print("=" * 50)
    
    try:
        db = next(get_db())
        
        # Count total agent logs
        total_logs = db.query(AgentLog).count()
        print(f"📊 Total Agent Logs: {total_logs}")
        
        if total_logs == 0:
            print("❌ No agent logs found in database!")
            return False
        
        # Count by agent type
        agent_types = ['validator', 'account_setup', 'scheduler', 'notifier']
        
        for agent_type in agent_types:
            count = db.query(AgentLog).filter(AgentLog.agent_type == agent_type).count()
            success_count = db.query(AgentLog).filter(
                AgentLog.agent_type == agent_type,
                AgentLog.status == 'success'
            ).count()
            failed_count = db.query(AgentLog).filter(
                AgentLog.agent_type == agent_type,
                AgentLog.status == 'failed'
            ).count()
            
            print(f"🤖 {agent_type}:")
            print(f"   Total: {count}")
            print(f"   Success: {success_count}")
            print(f"   Failed: {failed_count}")
        
        # Show recent logs
        print("\n📋 Recent Agent Logs (Last 5):")
        recent_logs = db.query(AgentLog).order_by(AgentLog.created_at.desc()).limit(5).all()
        
        for log in recent_logs:
            print(f"   {log.created_at.strftime('%H:%M:%S')} | {log.agent_type} | {log.action} | {log.status}")
            if log.error_message:
                print(f"      Error: {log.error_message}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_workflow_logs():
    """Check workflow and employee data"""
    print("\n🔍 Checking Workflow Data")
    print("=" * 30)
    
    try:
        db = next(get_db())
        
        total_employees = db.query(Employee).count()
        total_workflows = db.query(OnboardingWorkflow).count()
        
        print(f"👥 Total Employees: {total_employees}")
        print(f"🔄 Total Workflows: {total_workflows}")
        
        # Recent workflows
        recent_workflows = db.query(OnboardingWorkflow).order_by(
            OnboardingWorkflow.created_at.desc()
        ).limit(3).all()
        
        print("\n📋 Recent Workflows:")
        for workflow in recent_workflows:
            employee = db.query(Employee).filter(Employee.id == workflow.employee_id).first()
            print(f"   {workflow.created_at.strftime('%H:%M:%S')} | {employee.name if employee else 'Unknown'} | {workflow.status}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to check workflow data: {e}")
        return False

if __name__ == "__main__":
    print("🔍 AGENT LOGS DIAGNOSTIC")
    print("=" * 60)
    
    logs_exist = check_agent_logs()
    workflows_exist = check_workflow_logs()
    
    if logs_exist:
        print("\n✅ Agent logs are being written to database")
        print("   The issue might be in the API endpoint or audit service initialization")
    else:
        print("\n❌ No agent logs found!")
        print("   This suggests agents aren't logging their execution properly")
    
    print("\n💡 Next steps:")
    if not logs_exist:
        print("   1. Check if agents are actually executing their process() methods")
        print("   2. Verify database connection in agents")
        print("   3. Check for logging errors in agent execution")
    else:
        print("   1. Check audit service initialization in main.py")
        print("   2. Verify API endpoint is reading from correct database")
        print("   3. Test the /api/v1/audit/agent-performance/ endpoints directly")