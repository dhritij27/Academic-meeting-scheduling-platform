"""
test_api.py - API Testing Script
Tests all CRUD operations and complex queries
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"✓ {title}")
    print(f"{'='*60}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_auth():
    """Test authentication endpoints."""
    print("\n\n📌 TESTING AUTHENTICATION")
    
    # Login
    payload = {
        "email": "alice@university.edu",
        "role": "student"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    print_response("Login User", response)
    
    # Register
    payload = {
        "name": "Test User",
        "email": "test@university.edu",
        "role": "student"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=payload)
    print_response("Register New User", response)

def test_users():
    """Test user endpoints."""
    print("\n\n📌 TESTING USERS")
    
    # Get user
    response = requests.get(f"{BASE_URL}/users/1")
    print_response("Get User #1", response)
    
    # Create user
    payload = {
        "name": "New Student",
        "email": "newstudent@university.edu",
        "role": "student"
    }
    response = requests.post(f"{BASE_URL}/users", json=payload)
    print_response("Create New User", response)

def test_meetings():
    """Test meeting endpoints."""
    print("\n\n📌 TESTING MEETINGS")
    
    # Get upcoming meetings
    response = requests.get(f"{BASE_URL}/meetings/upcoming?user_id=1&limit=5")
    print_response("Get Upcoming Meetings for User #1", response)
    
    # Get meeting details
    response = requests.get(f"{BASE_URL}/meetings/1")
    print_response("Get Meeting #1 Details", response)
    
    # Create meeting
    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    payload = {
        "title": "API Test Meeting",
        "description": "Testing the new API",
        "room_id": 1,
        "slot_id": 1,
        "meeting_date": tomorrow,
        "created_by": 1,
        "participants": [2, 3]
    }
    response = requests.post(f"{BASE_URL}/meetings", json=payload)
    print_response("Create New Meeting", response)

def test_search():
    """Test advanced search."""
    print("\n\n📌 TESTING ADVANCED SEARCH")
    
    payload = {
        "title_keyword": "Meeting",
        "status": "scheduled"
    }
    response = requests.post(f"{BASE_URL}/meetings/search", json=payload)
    print_response("Search Meetings (by keyword)", response)

def test_rooms():
    """Test room endpoints."""
    print("\n\n📌 TESTING ROOMS")
    
    # Get all rooms
    response = requests.get(f"{BASE_URL}/rooms")
    print_response("Get All Rooms", response)
    
    # Get available rooms
    test_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = requests.get(
        f"{BASE_URL}/rooms/available",
        params={
            "date": test_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
    )
    print_response("Get Available Rooms", response)

def test_timeslots():
    """Test time slot endpoints."""
    print("\n\n📌 TESTING TIME SLOTS")
    
    # Get all slots
    response = requests.get(f"{BASE_URL}/timeslots")
    print_response("Get All Time Slots", response)
    
    # Get available slots for user
    test_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = requests.get(
        f"{BASE_URL}/timeslots/available",
        params={
            "user_id": 1,
            "date": test_date
        }
    )
    print_response("Get Available Slots for User #1", response)

def test_participant_response():
    """Test participant response endpoint."""
    print("\n\n📌 TESTING PARTICIPANT RESPONSE")
    
    payload = {
        "user_id": 2,
        "response": "accepted"
    }
    response = requests.post(f"{BASE_URL}/meetings/1/respond", json=payload)
    print_response("Accept Meeting Invitation", response)

def test_schedule():
    """Test user schedule endpoint."""
    print("\n\n📌 TESTING USER SCHEDULE")
    
    start_date = date.today().strftime('%Y-%m-%d')
    end_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = requests.get(
        f"{BASE_URL}/user/1/schedule",
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    print_response("Get User #1 Schedule (7 days)", response)

def test_analytics():
    """Test analytics endpoint."""
    print("\n\n📌 TESTING ANALYTICS")
    
    start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = date.today().strftime('%Y-%m-%d')
    
    response = requests.get(
        f"{BASE_URL}/analytics/meetings",
        params={
            "start_date": start_date,
            "end_date": end_date
        }
    )
    print_response("Get Meeting Analytics (30 days)", response)

def test_delete():
    """Test delete endpoint."""
    print("\n\n📌 TESTING DELETE OPERATIONS")
    
    # First, create a meeting to delete
    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    payload = {
        "title": "Meeting to Delete",
        "description": "This will be deleted",
        "room_id": 1,
        "slot_id": 2,
        "meeting_date": tomorrow,
        "created_by": 1,
        "participants": []
    }
    create_response = requests.post(f"{BASE_URL}/meetings", json=payload)
    meeting_data = create_response.json()
    
    if meeting_data['status'] == 'success':
        meeting_id = meeting_data['meeting_id']
        
        # Delete the meeting
        response = requests.delete(f"{BASE_URL}/meetings/{meeting_id}")
        print_response(f"Delete Meeting #{meeting_id}", response)

def test_health():
    """Test health check."""
    print("\n\n📌 TESTING HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    print_response("API Health Check", response)

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🚀 ACADEMIC MEETING SCHEDULER - API TEST SUITE")
    print("="*60)
    
    try:
        # Test in order of dependency
        test_health()
        test_auth()
        test_users()
        test_meetings()
        test_rooms()
        test_timeslots()
        test_search()
        test_participant_response()
        test_schedule()
        test_analytics()
        test_delete()
        
        print("\n\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the backend server is running on http://localhost:5000")
        print("Run: python backend/app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == '__main__':
    main()
