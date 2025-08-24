#!/usr/bin/env python3
"""
Database Migration: Make workflow_id nullable in agent_logs table
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import engine
from sqlalchemy import text

def migrate_agent_logs():
    """Migrate agent_logs table to make workflow_id nullable"""
    print("🔄 Migrating agent_logs table...")
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if constraint exists and drop it
                print("   📋 Checking foreign key constraint...")
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.table_constraints 
                    WHERE constraint_name = 'agent_logs_workflow_id_fkey' 
                    AND table_name = 'agent_logs'
                """))
                
                if result.scalar() > 0:
                    print("   🗑️  Dropping foreign key constraint...")
                    conn.execute(text("""
                        ALTER TABLE agent_logs 
                        DROP CONSTRAINT IF EXISTS agent_logs_workflow_id_fkey
                    """))
                
                # Make workflow_id nullable
                print("   📝 Making workflow_id nullable...")
                conn.execute(text("""
                    ALTER TABLE agent_logs 
                    ALTER COLUMN workflow_id DROP NOT NULL
                """))
                
                # Re-add foreign key constraint (nullable)
                print("   🔗 Re-adding foreign key constraint...")
                conn.execute(text("""
                    ALTER TABLE agent_logs 
                    ADD CONSTRAINT agent_logs_workflow_id_fkey 
                    FOREIGN KEY (workflow_id) 
                    REFERENCES onboarding_workflows(id)
                """))
                
                # Commit transaction
                trans.commit()
                print("   ✅ Migration completed successfully!")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"   ❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🗄️  AGENT LOGS MIGRATION")
    print("=" * 40)
    
    success = migrate_agent_logs()
    
    if success:
        print("\n✅ Database migration completed!")
        print("   Agent logs can now be created without workflow references")
    else:
        print("\n❌ Migration failed!")
        print("   Please check the error messages above")