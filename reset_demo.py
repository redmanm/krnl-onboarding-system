#!/usr/bin/env python3
"""
Quick script to reset the database for demo purposes
"""
import requests
import sys

API_BASE_URL = "http://localhost:8000"

def reset_database():
    """Delete all employees and related data"""
    try:
        print("🔄 Resetting database...")
        
        # Call the delete all employees endpoint
        response = requests.delete(f"{API_BASE_URL}/api/v1/employees/all?confirm=true")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Database reset successful!")
            print(f"   Deleted {result.get('deleted_counts', {}).get('employees', 0)} employees")
            print(f"   Deleted {result.get('deleted_counts', {}).get('workflows', 0)} workflows")
            print("📊 Dashboard is now ready for demo with 0 employees")
        else:
            print(f"❌ Reset failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API server")
        print("   Make sure the backend is running on http://localhost:8000")
        print("   Run: docker-compose up -d")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_status():
    """Check current database status"""
    try:
        print("📊 Checking current status...")
        
        # Get dashboard stats
        response = requests.get(f"{API_BASE_URL}/api/v1/dashboard/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total employees: {stats.get('total_employees', 0)}")
            print(f"   Pending: {stats.get('pending_onboarding', 0)}")
            print(f"   Completed: {stats.get('completed_onboarding', 0)}")
            print(f"   Failed: {stats.get('failed_onboarding', 0)}")
        else:
            print(f"❌ Status check failed: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API server")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎬 KRNL Onboarding System - Demo Reset Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_status()
    else:
        print("This will delete ALL employee data from the database.")
        confirm = input("Type 'yes' to confirm: ")
        
        if confirm.lower() == 'yes':
            reset_database()
        else:
            print("❌ Reset cancelled")
    
    print("\n🎯 Ready for demo!")
    print("   Frontend: http://localhost:3000")
    print("   API: http://localhost:8000")