"""
add_indexes.py - Add database indexes for performance optimization
Run this script after schema creation to add all necessary indexes
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_indexes():
    """Create all database indexes."""
    
    connection = None
    cursor = None
    
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            database=os.getenv('MYSQL_DATABASE', 'academic_meetings'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        
        cursor = connection.cursor()
        
        indexes = [
            # User indexes
            ("users", "idx_email", "CREATE INDEX idx_email ON users(email)"),
            ("users", "idx_role", "CREATE INDEX idx_role ON users(role)"),
            
            # Meeting indexes
            ("meetings", "idx_meeting_date", "CREATE INDEX idx_meeting_date ON meetings(meeting_date)"),
            ("meetings", "idx_created_by", "CREATE INDEX idx_created_by ON meetings(created_by)"),
            ("meetings", "idx_room_id", "CREATE INDEX idx_room_id ON meetings(room_id)"),
            ("meetings", "idx_status", "CREATE INDEX idx_status ON meetings(status)"),
            ("meetings", "idx_meeting_date_status", "CREATE INDEX idx_meeting_date_status ON meetings(meeting_date, status)"),
            
            # Meeting participants indexes
            ("meeting_participants", "idx_user_id", "CREATE INDEX idx_user_id ON meeting_participants(user_id)"),
            ("meeting_participants", "idx_response", "CREATE INDEX idx_response ON meeting_participants(response)"),
            ("meeting_participants", "idx_user_response", "CREATE INDEX idx_user_response ON meeting_participants(user_id, response)"),
            
            # User availability indexes
            ("user_availability", "idx_user_id_avail", "CREATE INDEX idx_user_id_avail ON user_availability(user_id)"),
            ("user_availability", "idx_slot_id", "CREATE INDEX idx_slot_id ON user_availability(slot_id)"),
            ("user_availability", "idx_is_available", "CREATE INDEX idx_is_available ON user_availability(is_available)"),
            
            # Time slots indexes
            ("time_slots", "idx_day_of_week", "CREATE INDEX idx_day_of_week ON time_slots(day_of_week)"),
            ("time_slots", "idx_is_recurring", "CREATE INDEX idx_is_recurring ON time_slots(is_recurring)"),
            
            # Meeting rooms indexes
            ("meeting_rooms", "idx_is_active", "CREATE INDEX idx_is_active ON meeting_rooms(is_active)"),
        ]
        
        print("\n" + "="*60)
        print("Creating Database Indexes")
        print("="*60 + "\n")
        
        created_count = 0
        skipped_count = 0
        
        for table, index_name, index_query in indexes:
            try:
                cursor.execute(index_query)
                connection.commit()
                print(f"✓ Created index: {index_name} on {table}")
                created_count += 1
            except Error as e:
                if "Duplicate key name" in str(e):
                    print(f"⊘ Index already exists: {index_name}")
                    skipped_count += 1
                else:
                    print(f"✗ Error creating index {index_name}: {e}")
        
        print("\n" + "="*60)
        print(f"Indexes Created: {created_count}")
        print(f"Indexes Skipped: {skipped_count}")
        print("="*60 + "\n")
        
        # Show all indexes
        print("Verifying indexes created:\n")
        cursor.execute("""
            SELECT DISTINCT INDEX_NAME, TABLE_NAME 
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND INDEX_NAME NOT IN ('PRIMARY')
            ORDER BY TABLE_NAME, INDEX_NAME
        """)
        
        for index_name, table_name in cursor.fetchall():
            print(f"  • {table_name}.{index_name}")
        
        print("\n✅ Index creation completed!\n")
        
    except Error as e:
        print(f"❌ Database error: {e}")
        raise
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    create_indexes()
