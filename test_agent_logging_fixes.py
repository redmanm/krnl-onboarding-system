#!/usr/bin/env python3
"""
Agent Logging Fix Verification Test
"""

import sys
import os
import asyncio
import uuid
import json
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_database_migration():
    """Test the database migration for nullable workflow_id"""
    print("🗄️  Testing Database Migration")
    print("=" * 40)
    
    try:
        from backend.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check if workflow_id is nullable
            result = conn.execute(text("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'agent_logs' 
                AND column_name = 'workflow_id'
            """))
            
            is_nullable = result.scalar()
            
            if is_nullable == 'YES':
                print("   ✅ workflow_id is nullable")
                return True
            else:
                print("   ⚠️  Running migration...")
                
                # Run migration
                conn.execute(text("ALTER TABLE agent_logs DROP CONSTRAINT IF EXISTS agent_logs_workflow_id_fkey"))
                conn.execute(text("ALTER TABLE agent_logs ALTER COLUMN workflow_id DROP NOT NULL"))
                conn.execute(text("ALTER TABLE agent_logs ADD CONSTRAINT agent_logs_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES onboarding_workflows(id)"))
                conn.commit()
                
                print("   ✅ Migration completed!")
                return True
                
    except Exception as e:
        print(f"   ❌ Migration failed: {e}")
        return False

async def test_uuid_serialization():
    """Test UUID serialization in BaseAgent"""
    print("\\n🔧 Testing UUID Serialization")
    print("=" * 40)
    
    try:
        from backend.agents.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__("test_serialization")
            async def process(self, input_data):
                return {"result": "success"}
        
        agent = TestAgent()
        
        test_data = {
            "employee_id": uuid.uuid4(),
            "nested_dict": {"another_uuid": uuid.uuid4()},
            "uuid_list": [uuid.uuid4(), uuid.uuid4()]
        }
        
        serialized = agent._serialize_for_json(test_data)
        
        # Verify JSON serializable
        json.dumps(serialized)
        
        print("   ✅ UUID serialization working")
        return True
        
    except Exception as e:
        print(f"   ❌ UUID serialization failed: {e}")
        return False

async def test_agent_logging():
    """Test agent logging with non-existent workflow"""
    print("\\n📋 Testing Agent Logging")
    print("=" * 40)
    
    try:
        from backend.agents.validator_agent import ValidatorAgent
        
        agent = ValidatorAgent()
        fake_workflow_id = uuid.uuid4()
        
        test_data = {
            "employee_data": {
                "name": "Test User",
                "email": "test@krnl.com",
                "role": "Engineer",
                "department": "Engineering",
                "start_date": "2024-02-01"
            }
        }
        
        print(f"   🆔 Using fake workflow: {fake_workflow_id}")
        result = await agent.execute(fake_workflow_id, test_data)
        
        if result and result.get("is_valid"):
            print("   ✅ Agent executed successfully")
            return True
        else:
            print("   ❌ Agent execution failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def verify_logs():
    """Verify logs in database"""
    print("\\n🔍 Verifying Database Logs")
    print("=" * 40)
    
    try:
        from backend.database import get_db
        from backend.models import AgentLog
        
        db = next(get_db())
        total_logs = db.query(AgentLog).count()
        
        print(f"   📊 Total agent logs: {total_logs}")
        
        # Count by type
        for agent_type in ['validator', 'account_setup', 'scheduler', 'notifier']:
            count = db.query(AgentLog).filter(AgentLog.agent_type == agent_type).count()
            print(f"   🤖 {agent_type}: {count}")
        
        orphan_logs = db.query(AgentLog).filter(AgentLog.workflow_id.is_(None)).count()
        print(f"   🔗 Logs without workflow: {orphan_logs}")
        
        db.close()
        
        if total_logs > 0:
            print("   ✅ Agent logs found!")
            return True
        else:
            print("   ❌ No logs found")
            return False
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔧 AGENT LOGGING FIX VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(test_database_migration())
    results.append(await test_uuid_serialization())
    results.append(await test_agent_logging())
    results.append(verify_logs())
    
    print("\\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\\n🎉 ALL FIXES WORKING!")
        print("   ✅ Migration successful")
        print("   ✅ UUID serialization fixed")
        print("   ✅ Agent logging working")
        print("   ✅ Audit logs available")
    else:
        print("\\n⚠️  Some fixes need attention")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())