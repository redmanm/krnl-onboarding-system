#!/usr/bin/env python3
"""
Direct Agent Execution Test
Tests individual agent execution to isolate the logging issue
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_direct_agent_execution():
    """Test direct execution of each agent"""
    print("🧪 DIRECT AGENT EXECUTION TEST")
    print("=" * 50)
    
    try:
        from backend.agents.validator_agent import ValidatorAgent
        from backend.agents.account_setup_agent import AccountSetupAgent
        from backend.agents.scheduler_agent import SchedulerAgent
        from backend.agents.notifier_agent import NotifierAgent
        
        # Test data
        test_workflow_id = uuid.uuid4()
        test_employee_id = uuid.uuid4()
        
        test_data = {
            "employee_data": {
                "name": "Direct Test User",
                "email": "direct.test@krnl.com",
                "role": "Software Engineer", 
                "department": "Engineering",
                "start_date": "2024-02-01"
            },
            "employee_id": test_employee_id
        }
        
        print(f"🆔 Test Workflow ID: {test_workflow_id}")
        print(f"👤 Test Employee ID: {test_employee_id}")
        
        # Test each agent individually
        agents_to_test = [
            ("ValidatorAgent", ValidatorAgent()),
            ("AccountSetupAgent", AccountSetupAgent()),
            ("SchedulerAgent", SchedulerAgent()),
            ("NotifierAgent", NotifierAgent())
        ]
        
        accumulated_data = test_data.copy()
        
        for agent_name, agent in agents_to_test:
            print(f"\n🤖 Testing {agent_name}...")
            
            try:
                print(f"   📤 Calling execute() method...")
                
                # This should trigger the BaseAgent.execute() method 
                # which should call process() and then _log_execution()
                result = await agent.execute(test_workflow_id, accumulated_data)
                
                print(f"   ✅ Agent execution completed")
                print(f"   📊 Result keys: {list(result.keys()) if result else 'None'}")
                
                # Add result to accumulated data for next agent
                if result:
                    accumulated_data[f"{agent_name.lower()}_result"] = result
                    
                    # Special data handling (from orchestrator logic)
                    if agent_name == "AccountSetupAgent":
                        accumulated_data["account_data"] = result.get("account_details", {})
                        accumulated_data["username"] = result.get("username", "")
                    elif agent_name == "SchedulerAgent":
                        accumulated_data["calendar_data"] = {"events": result.get("events", [])}
                
            except Exception as e:
                print(f"   ❌ Agent execution failed: {e}")
                print(f"   🔍 Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 Final accumulated data keys: {list(accumulated_data.keys())}")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

async def test_base_agent_logging():
    """Test BaseAgent logging functionality directly"""
    print(f"\n🔍 Testing BaseAgent Logging Directly")
    print("=" * 45)
    
    try:
        from backend.agents.base_agent import BaseAgent
        from backend.models import AgentLog
        from backend.database import get_db
        
        # Create a minimal test agent
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__("test_agent")
            
            async def process(self, input_data):
                return {"test": "success", "processed": True}
        
        # Test the agent
        test_agent = TestAgent()
        test_workflow_id = uuid.uuid4()
        test_data = {"test": "data"}
        
        print(f"   🆔 Test Workflow ID: {test_workflow_id}")
        
        # Execute the agent
        print("   📤 Executing test agent...")
        result = await test_agent.execute(test_workflow_id, test_data)
        
        print(f"   ✅ Execution completed: {result}")
        
        # Check if log was created
        print("   🔍 Checking database for log entry...")
        db = next(get_db())
        try:
            logs = db.query(AgentLog).filter(
                AgentLog.workflow_id == test_workflow_id
            ).all()
            
            if logs:
                log = logs[0]
                print(f"   ✅ Agent log found!")
                print(f"      Log ID: {log.id}")
                print(f"      Agent Type: {log.agent_type}")
                print(f"      Status: {log.status}")
                print(f"      Execution Time: {log.execution_time_ms}ms")
            else:
                print(f"   ❌ No agent log found in database!")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ BaseAgent logging test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_database_connection():
    """Test database connection for agent logging"""
    print(f"\n🗄️  Testing Database Connection")
    print("=" * 35)
    
    try:
        from backend.database import get_db
        from backend.models import AgentLog
        
        print("   📡 Testing database connection...")
        db = next(get_db())
        
        try:
            # Test query
            count = db.query(AgentLog).count()
            print(f"   ✅ Database connected! Current agent logs: {count}")
            
            # Test write
            print("   📝 Testing database write...")
            test_log = AgentLog(
                workflow_id=uuid.uuid4(),
                agent_type="connection_test",
                action="test_write",
                input_data={"test": True},
                output_data={"success": True},
                status="success",
                execution_time_ms=1
            )
            
            db.add(test_log)
            db.commit()
            print(f"   ✅ Database write successful! Log ID: {test_log.id}")
            
            # Clean up test log
            db.delete(test_log)
            db.commit()
            print(f"   🧹 Test log cleaned up")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    async def main():
        # Test database connectivity first
        await test_database_connection()
        
        # Test BaseAgent logging directly
        await test_base_agent_logging()
        
        # Test direct agent execution
        await test_direct_agent_execution()
        
        print("\n" + "=" * 60)
        print("🎯 CONCLUSIONS")
        print("=" * 60)
        print("If all tests pass but orchestrator doesn't create logs:")
        print("1. Issue is in orchestrator workflow execution")
        print("2. Agents are being bypassed during normal workflows")
        print("3. Exception handling is swallowing agent calls")
        print("\nIf BaseAgent logging test fails:")
        print("1. Database connection issues in agent context")
        print("2. Agent logging implementation problems")
        print("3. Session management issues")
    
    asyncio.run(main())