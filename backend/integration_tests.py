"""
integration_tests.py - Integration Tests for Critical Workflows
Tests complete user workflows end-to-end
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import db
from datetime import date, timedelta

class IntegrationTestCase(unittest.TestCase):
    """Base test case with common setup/teardown."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database."""
        print("\n" + "="*60)
        print("Setting up integration tests")
        print("="*60)
    
    def setUp(self):
        """Setup for each test."""
        self.test_date = date.today() + timedelta(days=1)
    
    def tearDown(self):
        """Cleanup after each test."""
        pass

class UserWorkflowTests(IntegrationTestCase):
    """Test user-related workflows."""
    
    def test_create_and_retrieve_user(self):
        """Test creating a user and retrieving it."""
        print("\n✓ Testing: Create and retrieve user")
        
        # Create user
        user_id = db.create_user(
            name="Test User",
            email="test.integration@university.edu",
            role="student"
        )
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)
        
        # Retrieve user
        user = db.get_user(user_id=user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], "test.integration@university.edu")
        self.assertEqual(user['role'], "student")
        
        print(f"  Created user: {user['name']} (ID: {user_id})")

class MeetingWorkflowTests(IntegrationTestCase):
    """Test meeting-related workflows."""
    
    def setUp(self):
        """Setup for meeting tests."""
        super().setUp()
        
        # Create test users
        self.user1_id = db.create_user("User 1", "user1.test@university.edu", "student")
        self.user2_id = db.create_user("User 2", "user2.test@university.edu", "professor")
    
    def test_create_meeting_and_get_details(self):
        """Test creating a meeting and getting its details."""
        print("\n✓ Testing: Create meeting and get details")
        
        # Create meeting
        meeting_id = db.create_meeting(
            title="Integration Test Meeting",
            description="Testing meeting creation",
            room_id=1,
            slot_id=1,
            meeting_date=self.test_date,
            created_by=self.user1_id,
            participants=[self.user2_id]
        )
        self.assertIsNotNone(meeting_id)
        self.assertGreater(meeting_id, 0)
        
        # Get meeting details
        meeting = db.get_meeting_details_with_participants(meeting_id)
        self.assertIsNotNone(meeting)
        self.assertEqual(meeting['title'], "Integration Test Meeting")
        
        print(f"  Created meeting: {meeting['title']} (ID: {meeting_id})")
    
    def test_get_upcoming_meetings(self):
        """Test retrieving upcoming meetings."""
        print("\n✓ Testing: Get upcoming meetings")
        
        # Create a meeting
        meeting_id = db.create_meeting(
            title="Upcoming Meeting",
            description="Testing",
            room_id=1,
            slot_id=1,
            meeting_date=self.test_date,
            created_by=self.user1_id,
            participants=[self.user2_id]
        )
        
        # Get upcoming meetings
        meetings = db.get_upcoming_meetings(user_id=self.user1_id, limit=10)
        self.assertIsNotNone(meetings)
        self.assertGreater(len(meetings), 0)
        
        print(f"  Found {len(meetings)} upcoming meetings")
    
    def test_search_meetings(self):
        """Test searching for meetings."""
        print("\n✓ Testing: Search meetings")
        
        # Create a meeting
        db.create_meeting(
            title="Searchable Meeting",
            description="For searching",
            room_id=1,
            slot_id=1,
            meeting_date=self.test_date,
            created_by=self.user1_id,
            participants=[]
        )
        
        # Search meetings
        search_params = {
            'title_keyword': 'Searchable',
            'status': 'scheduled'
        }
        meetings = db.search_meetings(search_params)
        self.assertIsNotNone(meetings)
        
        print(f"  Search found {len(meetings)} meeting(s)")

class ParticipantWorkflowTests(IntegrationTestCase):
    """Test participant-related workflows."""
    
    def setUp(self):
        """Setup for participant tests."""
        super().setUp()
        
        # Create test users
        self.user1_id = db.create_user("User 1", "participant1@university.edu", "student")
        self.user2_id = db.create_user("User 2", "participant2@university.edu", "student")
        
        # Create test meeting
        self.meeting_id = db.create_meeting(
            title="Participant Test Meeting",
            description="Testing participants",
            room_id=1,
            slot_id=1,
            meeting_date=self.test_date,
            created_by=self.user1_id,
            participants=[self.user2_id]
        )
    
    def test_update_participant_response(self):
        """Test updating participant response."""
        print("\n✓ Testing: Update participant response")
        
        # Update response
        success = db.update_participant_response(
            meeting_id=self.meeting_id,
            user_id=self.user2_id,
            response='accepted'
        )
        self.assertTrue(success)
        
        print(f"  Participant response updated successfully")

class AvailabilityWorkflowTests(IntegrationTestCase):
    """Test availability-related workflows."""
    
    def setUp(self):
        """Setup for availability tests."""
        super().setUp()
        self.user_id = db.create_user("User 3", "availability@university.edu", "student")
    
    def test_get_available_time_slots(self):
        """Test getting available time slots for a user."""
        print("\n✓ Testing: Get available time slots")
        
        # Get available slots
        available_slots = db.get_available_time_slots(self.user_id, self.test_date)
        self.assertIsNotNone(available_slots)
        
        print(f"  Found {len(available_slots)} available slots")

class AnalyticsWorkflowTests(IntegrationTestCase):
    """Test analytics workflows."""
    
    def test_get_meeting_analytics(self):
        """Test retrieving meeting analytics."""
        print("\n✓ Testing: Get meeting analytics")
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        # Get analytics
        analytics = db.get_meeting_analytics(start_date, end_date)
        self.assertIsNotNone(analytics)
        self.assertIn('counts', analytics)
        self.assertIn('top_organizers', analytics)
        
        print(f"  Analytics retrieved successfully")

def run_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("🧪 RUNNING INTEGRATION TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(UserWorkflowTests))
    suite.addTests(loader.loadTestsFromTestCase(MeetingWorkflowTests))
    suite.addTests(loader.loadTestsFromTestCase(ParticipantWorkflowTests))
    suite.addTests(loader.loadTestsFromTestCase(AvailabilityWorkflowTests))
    suite.addTests(loader.loadTestsFromTestCase(AnalyticsWorkflowTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60 + "\n")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
