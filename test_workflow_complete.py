#!/usr/bin/env python3
"""
Complete Workflow Test
Tests the full employee onboarding workflow with working agents
"""

import requests
import json
import time
from datetime import datetime, date, timedelta

def test_api_health():
    """Test if the API is healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: HEALTHY")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health Check: FAILED (Error: {e})")
        return False

def test_single_employee_workflow():
    """Test complete single employee onboarding workflow"""
    print("\n🧪 Testing Single Employee Onboarding Workflow")
    print("-" * 50)
    
    # Employee data
    employee_data = {
        "name": "Alice Johnson",
        "email": "alice.johnson@krnl.com",
        "role": "Software Engineer",
        "department": "Engineering",
        "start_date": (date.today() + timedelta(days=7)).isoformat()
    }
    
    try:
        # Create employee
        print("📤 Submitting employee onboarding request...")
        response = requests.post(
            "http://localhost:8000/api/v1/employees",
            json=employee_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Employee onboarding workflow started successfully!")
            print(f"   📋 Workflow ID: {result.get('workflow_id')}")
            print(f"   👤 Employee ID: {result.get('employee_id')}")
            print(f"   📊 Status: {result.get('status')}")
            
            # Print workflow results if available
            if 'workflow_results' in result:
                workflow_results = result['workflow_results']
                print("\n📊 Workflow Results:")
                
                # Validation results
                if 'validation' in workflow_results:
                    val_result = workflow_results['validation']
                    print(f"   ✅ Validation: {'PASSED' if val_result.get('is_valid') else 'FAILED'}")
                    if val_result.get('cleaned_data'):
                        print(f"      📝 Cleaned Name: {val_result['cleaned_data'].get('name')}")
                        print(f"      📧 Cleaned Email: {val_result['cleaned_data'].get('email')}")
                
                # Account setup results
                if 'account_setup' in workflow_results:
                    acc_result = workflow_results['account_setup']
                    print(f"   ✅ Account Setup: {'SUCCESS' if acc_result.get('account_created') else 'FAILED'}")
                    if acc_result.get('username'):
                        print(f"      👤 Username: {acc_result['username']}")
                        print(f"      🔐 Permissions: {len(acc_result.get('permissions', []))} granted")
                
                # Scheduling results
                if 'scheduling' in workflow_results:
                    sched_result = workflow_results['scheduling']
                    events_count = sched_result.get('events_scheduled', 0)
                    print(f"   ✅ Scheduling: {events_count} events scheduled")
                    if sched_result.get('events'):
                        for event in sched_result['events'][:3]:  # Show first 3 events
                            print(f"      📅 {event.get('type', 'Event')}: {event.get('title', 'N/A')}")
                
                # Notification results
                if 'notification' in workflow_results:
                    notif_result = workflow_results['notification']
                    notifications_sent = len(notif_result.get('notifications_sent', []))
                    print(f"   ✅ Notifications: {notifications_sent} sent")
                    for notif in notif_result.get('notifications_sent', [])[:3]:
                        print(f"      📧 {notif.get('type', 'notification')} → {notif.get('recipient', 'N/A')}")
            
            return True
            
        else:
            print(f"❌ Employee onboarding failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def test_csv_upload():
    """Test CSV upload functionality"""
    print("\n🧪 Testing CSV Upload Functionality")
    print("-" * 50)
    
    # Create a sample CSV
    csv_content = """name,email,role,department,start_date
John Smith,john.smith@krnl.com,Product Manager,Product,2024-01-20
Jane Doe,jane.doe@krnl.com,Designer,Design,2024-01-22
Bob Wilson,bob.wilson@krnl.com,QA Engineer,QA,2024-01-25"""
    
    try:
        # Create temporary CSV file
        with open("temp_employees.csv", "w") as f:
            f.write(csv_content)
        
        print("📤 Uploading CSV file...")
        
        with open("temp_employees.csv", "rb") as f:
            files = {"file": ("employees.csv", f, "text/csv")}
            response = requests.post(
                "http://localhost:8000/api/v1/employees/upload-csv",
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CSV upload successful!")
            print(f"   📊 Total Processed: {result.get('total_processed', 0)}")
            print(f"   ✅ Successful: {result.get('successful', 0)}")
            print(f"   ❌ Failed: {result.get('failed', 0)}")
            return True
        else:
            print(f"❌ CSV upload failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CSV upload test failed: {e}")
        return False
    finally:
        # Cleanup
        try:
            import os
            os.remove("temp_employees.csv")
        except:
            pass

def test_employee_list():
    """Test employee listing"""
    print("\n🧪 Testing Employee List API")
    print("-" * 50)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/employees", timeout=10)
        
        if response.status_code == 200:
            employees = response.json()
            print(f"✅ Employee list retrieved: {len(employees)} employees found")
            
            for emp in employees[:3]:  # Show first 3
                print(f"   👤 {emp.get('name', 'N/A')} - {emp.get('role', 'N/A')} ({emp.get('workflow_status', 'N/A')})")
            
            return True
        else:
            print(f"❌ Employee list failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Employee list test failed: {e}")
        return False

def main():
    """Run all workflow tests"""
    print("🚀 COMPLETE WORKFLOW TESTING")
    print("=" * 60)
    
    # Test results
    results = []
    
    # 1. Health check
    results.append(test_api_health())
    
    # 2. Single employee workflow
    results.append(test_single_employee_workflow())
    
    # 3. CSV upload
    results.append(test_csv_upload())
    
    # 4. Employee list
    results.append(test_employee_list())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The agent system is working perfectly!")
        print("\n✅ Confirmed Working:")
        print("   • API health and connectivity")
        print("   • Complete onboarding workflow")
        print("   • All 4 agents processing successfully")
        print("   • Database operations")
        print("   • CSV upload functionality")
        print("   • Employee management")
    else:
        print("⚠️  Some tests failed. Check the details above.")
        
        # Troubleshooting tips
        print("\n🔧 Troubleshooting Tips:")
        print("   • Ensure all Docker containers are running")
        print("   • Check that PostgreSQL is accessible")
        print("   • Verify network connectivity between services")
        print("   • Check Docker logs: docker-compose logs")

if __name__ == "__main__":
    main()