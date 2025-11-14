"""
seed_data.py - Database Seeding Script
Populates the database with realistic test data for development and testing.
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

class DataSeeder:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database."""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                database=os.getenv('MYSQL_DATABASE', 'academic_meetings'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                port=int(os.getenv('MYSQL_PORT', 3306))
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("✓ Connected to database successfully")
        except Error as e:
            print(f"✗ Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✓ Connection closed")
    
    def clear_tables(self):
        """Clear existing data from tables."""
        tables = [
            'student_grades',
            'fam_mentees',
            'fams',
            'students',
            'meeting_participants',
            'meetings',
            'user_availability',
            'time_slots',
            'meeting_rooms',
            'users'
        ]
        
        for table in tables:
            try:
                self.cursor.execute(f"DELETE FROM {table}")
                self.connection.commit()
                print(f"✓ Cleared {table}")
            except Error as e:
                print(f"✗ Error clearing {table}: {e}")
                self.connection.rollback()
    
    def seed_users(self):
        """Create sample users."""
        users = [
            ('Alice Johnson', 'alice@university.edu', 'student'),
            ('Bob Smith', 'bob@university.edu', 'student'),
            ('Charlie Brown', 'charlie@university.edu', 'student'),
            ('Diana Prince', 'diana@university.edu', 'student'),
            ('Evan Davis', 'evan@university.edu', 'student'),
            
            # Professors
            ('Dr. Rajesh Kumar', 'rajesh.kumar@university.edu', 'professor'),
            ('Dr. Priya Sharma', 'priya.sharma@university.edu', 'professor'),
            ('Dr. Suresh Patel', 'suresh.patel@university.edu', 'professor'),
            ('Dr. Anand Menon', 'anand.menon@university.edu', 'professor'),
            
            # FAMs (First-year Academic Mentors)
            ('Ishaan Gupta', 'ishaan.gupta@university.edu', 'professor'),
            ('Tanvi Das', 'tanvi.das@university.edu', 'professor'),
            ('Rohan Mehta', 'rohan.mehta@university.edu', 'professor'),
            ('Kavya Menon', 'kavya.menon@university.edu', 'professor'),
            ('Krishna Kumar', 'krishna.kumar@university.edu', 'professor'),
        ]
        
        user_ids = []
        query = "INSERT INTO users (name, email, role) VALUES (%s, %s, %s)"
        
        for name, email, role in users:
            try:
                self.cursor.execute(query, (name, email, role))
                user_ids.append(self.cursor.lastrowid)
                print(f"  ✓ Created user: {name} ({role})")
            except Error as e:
                print(f"  ✗ Error creating user {name}: {e}")
        
        self.connection.commit()
        print(f"✓ Created {len(user_ids)} users\n")
        return user_ids
    
    def seed_fams_and_students(self):
        """Seed FAMs and students with their relationships."""
        try:
            # Insert FAMs
            self.cursor.execute("""
                INSERT INTO fams (name, srn, department, year, specialization, bio, rating, max_mentees)
                VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s),
                    (%s, %s, %s, %s, %s, %s, %s, %s),
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    department = VALUES(department),
                    year = VALUES(year),
                    specialization = VALUES(specialization),
                    bio = VALUES(bio),
                    rating = VALUES(rating),
                    max_mentees = VALUES(max_mentees),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                'John Doe', 'FAM001', 'Computer Science', 3, 'Algorithms, Web Development', 
                'Senior CS student with experience in competitive programming', 4.8, 8,
                'Jane Smith', 'FAM002', 'Computer Science', 4, 'Machine Learning, Python', 
                'ML enthusiast with internship experience at top tech companies', 4.9, 10,
                'Alex Johnson', 'FAM003', 'Information Technology', 3, 'Cybersecurity, Networking', 
                'Cyber security researcher and CTF player', 4.7, 6
            ))
            
            # Insert Students
            self.cursor.execute("""
                INSERT INTO students (name, srn, department, year)
                VALUES 
                    (%s, %s, %s, %s),
                    (%s, %s, %s, %s),
                    (%s, %s, %s, %s),
                    (%s, %s, %s, %s),
                    (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    department = VALUES(department),
                    year = VALUES(year),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                'Michael Brown', 'SRN2023001', 'Computer Science', 1,
                'Sarah Wilson', 'SRN2023002', 'Computer Science', 1,
                'David Lee', 'SRN2023003', 'Information Technology', 1,
                'Emma Garcia', 'SRN2023004', 'Computer Science', 1,
                'James Miller', 'SRN2023005', 'Information Technology', 1
            ))
            
            # Assign students to FAMs
            self.cursor.execute("""
                INSERT INTO fam_mentees (fam_id, student_id)
                SELECT f.id, s.id 
                FROM (SELECT 'FAM001' as srn, 'SRN2023001' as student_srn
                      UNION SELECT 'FAM001', 'SRN2023002'
                      UNION SELECT 'FAM002', 'SRN2023003'
                      UNION SELECT 'FAM002', 'SRN2023004'
                      UNION SELECT 'FAM003', 'SRN2023005') as mappings
                JOIN fams f ON f.srn = mappings.srn
                JOIN students s ON s.srn = mappings.student_srn
                ON DUPLICATE KEY UPDATE assigned_at = CURRENT_TIMESTAMP
            """)
            
            # Insert sample grades
            self.cursor.execute("""
                INSERT INTO student_grades (student_id, subject_id, fam_id, grade, semester, academic_year, feedback)
                SELECT 
                    s.id,
                    sub.id,
                    fm.fam_id,
                    ELT(FLOOR(1 + RAND() * 5), 'A', 'B+', 'B', 'C+', 'C'),
                    'Fall',
                    '2024-2025',
                    CONCAT('Good progress in ', sub.subject_name, '. ', 
                           CASE 
                               WHEN RAND() > 0.7 THEN 'Excellent work!'
                               WHEN RAND() > 0.4 THEN 'Good performance.'
                               ELSE 'Needs improvement in some areas.'
                           END)
                FROM 
                    students s
                CROSS JOIN 
                    (SELECT id, subject_name FROM subjects ORDER BY RAND() LIMIT 3) sub
                JOIN 
                    fam_mentees fm ON s.id = fm.student_id
                ON DUPLICATE KEY UPDATE 
                    grade = VALUES(grade),
                    feedback = VALUES(feedback),
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            # Update mentee counts
            self.cursor.execute("""
                UPDATE fams f
                SET mentees = (
                    SELECT COUNT(*) 
                    FROM fam_mentees fm 
                    WHERE fm.fam_id = f.id
                )
            """)
            
            self.connection.commit()
            print("✓ Seeded FAMs, students, and their relationships")
            
            # Return the IDs of created FAMs and students for reference
            self.cursor.execute("SELECT id, srn, name FROM fams")
            fams = self.cursor.fetchall()
            self.cursor.execute("SELECT id, srn, name FROM students")
            students = self.cursor.fetchall()
            
            return fams, students
            
        except Error as e:
            print(f"✗ Error seeding FAMs and students: {e}")
            self.connection.rollback()
            raise

    def seed_rooms(self):
        """Create sample meeting rooms."""
        rooms = [
            ('Conference Room A', 10),
            ('Conference Room B', 8),
            ('Meeting Room 101', 4),
            ('Meeting Room 102', 4),
            ('Board Room', 15),
            ('Study Area 1', 2),
            ('Study Area 2', 2),
            ('Seminar Hall', 25),
        ]
        
        room_ids = []
        query = "INSERT INTO meeting_rooms (name, capacity) VALUES (%s, %s)"
        
        for name, capacity in rooms:
            try:
                self.cursor.execute(query, (name, capacity))
                room_ids.append(self.cursor.lastrowid)
                print(f"  ✓ Created room: {name}")
            except Error as e:
                print(f"  ✗ Error creating room {name}: {e}")
        
        self.connection.commit()
        print(f"✓ Created {len(room_ids)} rooms\n")
        return room_ids
    
    def seed_time_slots(self):
        """Create sample time slots."""
        time_slots = [
            ('09:00', '10:00', 'monday', True),
            ('10:00', '11:00', 'monday', True),
            ('11:00', '12:00', 'monday', True),
            ('14:00', '15:00', 'monday', True),
            ('15:00', '16:00', 'monday', True),
            
            ('09:00', '10:00', 'tuesday', True),
            ('10:00', '11:00', 'tuesday', True),
            ('11:00', '12:00', 'tuesday', True),
            ('14:00', '15:00', 'tuesday', True),
            ('15:00', '16:00', 'tuesday', True),
            
            ('09:00', '10:00', 'wednesday', True),
            ('10:00', '11:00', 'wednesday', True),
            ('11:00', '12:00', 'wednesday', True),
            ('14:00', '15:00', 'wednesday', True),
            ('15:00', '16:00', 'wednesday', True),
            
            ('09:00', '10:00', 'thursday', True),
            ('10:00', '11:00', 'thursday', True),
            ('11:00', '12:00', 'thursday', True),
            ('14:00', '15:00', 'thursday', True),
            ('15:00', '16:00', 'thursday', True),
            
            ('09:00', '10:00', 'friday', True),
            ('10:00', '11:00', 'friday', True),
            ('11:00', '12:00', 'friday', True),
            ('14:00', '15:00', 'friday', True),
            ('15:00', '16:00', 'friday', True),
        ]
        
        slot_ids = []
        query = "INSERT INTO time_slots (start_time, end_time, day_of_week, is_recurring) VALUES (%s, %s, %s, %s)"
        
        for start, end, day, recurring in time_slots:
            try:
                self.cursor.execute(query, (start, end, day, recurring))
                slot_ids.append(self.cursor.lastrowid)
            except Error as e:
                if "Duplicate entry" in str(e):
                    # Slot already exists, fetch its ID
                    fetch_query = "SELECT slot_id FROM time_slots WHERE start_time = %s AND day_of_week = %s"
                    self.cursor.execute(fetch_query, (start, day))
                    result = self.cursor.fetchone()
                    if result:
                        slot_ids.append(result['slot_id'])
                else:
                    print(f"  ✗ Error creating slot {start}-{end} on {day}: {e}")
        
        self.connection.commit()
        print(f"✓ Created/Retrieved {len(slot_ids)} time slots\n")
        return slot_ids
    
    def seed_user_availability(self, user_ids, slot_ids):
        """Create user availability records."""
        query = "INSERT INTO user_availability (user_id, slot_id, is_available) VALUES (%s, %s, %s)"
        
        availability_count = 0
        for user_id in user_ids[:10]:  # First 10 users
            # Randomly assign 5-8 available slots per user
            assigned_slots = random.sample(slot_ids, min(8, len(slot_ids)))
            for slot_id in assigned_slots:
                try:
                    self.cursor.execute(query, (user_id, slot_id, True))
                    availability_count += 1
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"  ✗ Error creating availability: {e}")
        
        self.connection.commit()
        print(f"✓ Created {availability_count} availability records\n")
    
    def seed_meetings(self, user_ids, room_ids, slot_ids):
        """Create sample meetings."""
        if len(user_ids) < 2 or len(room_ids) < 1 or len(slot_ids) < 1:
            print("✗ Not enough data to create meetings")
            return
        
        meetings = []
        today = date.today()
        
        # Create meetings for the next 14 days
        for day_offset in range(1, 15):
            meeting_date = today + timedelta(days=day_offset)
            
            # Ensure we have enough slot IDs
            if len(slot_ids) > 0:
                slot_id = random.choice(slot_ids)
                room_id = random.choice(room_ids)
                organizer = random.choice(user_ids[:5])  # Students as organizers
                
                title_templates = [
                    "Discussion on Project {topic}",
                    "{topic} Consultation",
                    "{topic} Session",
                    "Meeting with {topic}",
                    "{topic} Review"
                ]
                
                topics = [
                    "Data Structures",
                    "Web Development",
                    "Machine Learning",
                    "Database Design",
                    "Competitive Programming",
                    "Career Planning",
                    "Course Selection",
                    "Internship Preparation"
                ]
                
                title = random.choice(title_templates).format(topic=random.choice(topics))
                description = f"Meeting scheduled for discussion and guidance"
                
                meetings.append({
                    'title': title,
                    'description': description,
                    'room_id': room_id,
                    'slot_id': slot_id,
                    'meeting_date': meeting_date,
                    'created_by': organizer,
                    'status': 'scheduled'
                })
        
        query = """
        INSERT INTO meetings (title, description, room_id, slot_id, meeting_date, created_by, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        meeting_ids = []
        for meeting in meetings:
            try:
                self.cursor.execute(query, (
                    meeting['title'],
                    meeting['description'],
                    meeting['room_id'],
                    meeting['slot_id'],
                    meeting['meeting_date'],
                    meeting['created_by'],
                    meeting['status']
                ))
                meeting_ids.append(self.cursor.lastrowid)
            except Error as e:
                if "UNIQUE" not in str(e):
                    print(f"  ✗ Error creating meeting: {e}")
        
        self.connection.commit()
        print(f"✓ Created {len(meeting_ids)} meetings\n")
        return meeting_ids
    
    def seed_meeting_participants(self, meeting_ids, user_ids):
        """Add participants to meetings."""
        if not meeting_ids or len(user_ids) < 1:
            return
        
        query = """
        INSERT INTO meeting_participants (meeting_id, user_id, response)
        VALUES (%s, %s, %s)
        """
        
        participant_count = 0
        responses = ['accepted', 'pending', 'declined']
        
        for meeting_id in meeting_ids:
            # Add 2-4 random participants to each meeting
            num_participants = random.randint(2, min(4, len(user_ids)))
            participants = random.sample(user_ids, num_participants)
            
            for participant_id in participants:
                try:
                    response = random.choice(responses)
                    self.cursor.execute(query, (meeting_id, participant_id, response))
                    participant_count += 1
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"  ✗ Error adding participant: {e}")
        
        self.connection.commit()
        print(f"✓ Added {participant_count} meeting participants\n")
    
    def seed_all(self):
        """Run all seeding operations."""
        try:
            print("\n" + "="*50)
            print("Database Seeding Started")
            print("="*50 + "\n")
            
            print("1. Clearing existing data...")
            self.clear_tables()
            
            print("\n2. Seeding users...")
            user_ids = self.seed_users()
            
            print("3. Seeding FAMs and students...")
            self.seed_fams_and_students()
            
            print("4. Seeding meeting rooms...")
            room_ids = self.seed_rooms()
            
            print("5. Seeding time slots...")
            slot_ids = self.seed_time_slots()
            
            print("6. Seeding user availability...")
            self.seed_user_availability(user_ids, slot_ids)
            
            print("7. Seeding meetings...")
            meeting_ids = self.seed_meetings(user_ids, room_ids, slot_ids)
            
            print("8. Seeding meeting participants...")
            self.seed_meeting_participants(meeting_ids, user_ids)
            
            print("\n" + "="*50)
            print("✓ Database Seeding Completed Successfully!")
            print("="*50)
            print(f"\nSummary:")
            print(f"  • Users: {len(user_ids)}")
            print(f"  • Rooms: {len(room_ids)}")
            print(f"  • Time Slots: {len(slot_ids)}")
            print(f"  • Meetings: {len(meeting_ids)}")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error during seeding: {e}")
            raise

def main():
    seeder = DataSeeder()
    try:
        seeder.connect()
        seeder.seed_all()
    finally:
        seeder.close()

if __name__ == '__main__':
    main()
