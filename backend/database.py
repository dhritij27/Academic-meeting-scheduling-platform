import os
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import date, datetime
import json

# Load environment variables
load_dotenv()

class Database:
    _instance = None
    _connection_pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._initialize_pool()
        return cls._instance
    
    @classmethod
    def _initialize_pool(cls):
        """Initialize the connection pool."""
        try:
            cls._connection_pool = pooling.MySQLConnectionPool(
                pool_name="meeting_pool",
                pool_size=5,
                pool_reset_session=True,
                host=os.getenv('MYSQL_HOST', 'localhost'),
                database=os.getenv('MYSQL_DATABASE', 'academic_meetings'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                port=int(os.getenv('MYSQL_PORT', 3306))
            )
        except Error as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        try:
            return self._connection_pool.get_connection()
        except Error as e:
            print(f"Error getting connection from pool: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Execute a query and return the results."""
        connection = self.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            # Enable query optimization hints
            cursor.execute("SET SESSION optimizer_switch='derived_merge=on,subquery_materialization_cost_based=on'")
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result if result else []
            else:
                connection.commit()
                return cursor.lastrowid or cursor.rowcount
                
        except Error as e:
            print(f"Error executing query: {e}")
            connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def execute_complex_query(self, query: str, params: tuple = None, nested_results: bool = False):
        """Execute a complex query with support for nested results."""
        connection = self.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            # Enable optimization for complex queries
            cursor.execute("SET SESSION optimizer_switch='derived_merge=on,subquery_materialization_cost_based=on'")
            cursor.execute("SET SESSION join_buffer_size=262144")  # Optimize for complex joins
            
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            
            if not nested_results:
                return results if results else []
                
            # Process nested results if required
            processed_results = []
            for row in results:
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                        try:
                            processed_row[key] = json.loads(value)
                        except json.JSONDecodeError:
                            processed_row[key] = value
                    else:
                        processed_row[key] = value
                processed_results.append(processed_row)
            
            return processed_results
                
        except Error as e:
            print(f"Error executing complex query: {e}")
            connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    # User Management
    def get_user(self, user_id: int = None, email: str = None) -> Optional[Dict]:
        """Get a single user by ID or email."""
        if user_id:
            query = "SELECT * FROM users WHERE user_id = %s"
            result = self.execute_query(query, (user_id,))
        elif email:
            query = "SELECT * FROM users WHERE email = %s"
            result = self.execute_query(query, (email,))
        else:
            return None
        return result[0] if result else None
    
    def create_user(self, name: str, email: str, role: str) -> int:
        """Create a new user and return the user ID."""
        query = """
        INSERT INTO users (name, email, role)
        VALUES (%s, %s, %s)
        """
        return self.execute_query(query, (name, email, role), fetch=False)
    
    # Meeting Management
    def create_meeting(self, title: str, description: str, room_id: int, 
                      slot_id: int, meeting_date: date, created_by: int, 
                      participants: List[int] = None) -> int:
        """Create a new meeting and add participants."""
        # Start transaction
        connection = self.get_connection()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Create meeting
            query = """
            INSERT INTO meetings (title, description, room_id, slot_id, meeting_date, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (title, description, room_id, slot_id, meeting_date, created_by))
            meeting_id = cursor.lastrowid
            
            # Add participants
            if participants:
                participant_values = [(meeting_id, user_id, 'pending') for user_id in participants]
                cursor.executemany(
                    """
                    INSERT INTO meeting_participants (meeting_id, user_id, response)
                    VALUES (%s, %s, %s)
                    """,
                    participant_values
                )
            
            connection.commit()
            return meeting_id
            
        except Error as e:
            connection.rollback()
            print(f"Error creating meeting: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def get_upcoming_meetings(self, user_id: int = None, limit: int = 10) -> List[Dict]:
        """Get upcoming meetings, optionally filtered by user."""
        query = """
        SELECT m.*, u.name as organizer_name, mr.name as room_name,
               ts.start_time, ts.end_time, ts.day_of_week
        FROM meetings m
        JOIN users u ON m.created_by = u.user_id
        LEFT JOIN meeting_rooms mr ON m.room_id = mr.room_id
        JOIN time_slots ts ON m.slot_id = ts.slot_id
        WHERE m.meeting_date >= CURDATE()
        AND m.status = 'scheduled'
        """
        
        if user_id:
            query += """
            AND m.meeting_id IN (
                SELECT meeting_id FROM meeting_participants 
                WHERE user_id = %s AND response = 'accepted'
                UNION
                SELECT meeting_id FROM meetings WHERE created_by = %s
            )
            """
            params = (user_id, user_id)
        else:
            params = ()
        
        query += " ORDER BY m.meeting_date, ts.start_time LIMIT %s"
        return self.execute_query(query, params + (limit,))
    
    # Room Management
    def get_available_rooms(self, date: date, start_time: str, end_time: str) -> List[Dict]:
        """Get available rooms for a specific time slot."""
        query = """
        SELECT r.*
        FROM meeting_rooms r
        WHERE r.is_active = TRUE
        AND r.room_id NOT IN (
            SELECT m.room_id 
            FROM meetings m
            JOIN time_slots ts ON m.slot_id = ts.slot_id
            WHERE m.meeting_date = %s
            AND m.status != 'cancelled'
            AND (
                (ts.start_time < %s AND ts.end_time > %s) OR
                (ts.start_time < %s AND ts.end_time > %s) OR
                (ts.start_time >= %s AND ts.end_time <= %s)
            )
        )
        """
        return self.execute_query(
            query, 
            (date, end_time, start_time, start_time, end_time, start_time, end_time)
        )
    
    # Time Slot Management
    def get_available_time_slots(self, user_id: int, date: date) -> List[Dict]:
        """Get available time slots for a user on a specific date."""
        query = """
        SELECT ts.*
        FROM time_slots ts
        WHERE ts.slot_id NOT IN (
            -- Slots where user has other meetings
            SELECT m.slot_id
            FROM meetings m
            JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
            WHERE m.meeting_date = %s
            AND mp.user_id = %s
            AND mp.response = 'accepted'
            AND m.status != 'cancelled'
            
            UNION
            
            -- Slots where user is marked as unavailable
            SELECT ua.slot_id
            FROM user_availability ua
            WHERE ua.user_id = %s
            AND ua.is_available = FALSE
        )
        ORDER BY ts.start_time
        """
        return self.execute_query(query, (date, user_id, user_id))
    
    # Participant Management
    def update_participant_response(self, meeting_id: int, user_id: int, response: str) -> bool:
        """Update a participant's response to a meeting invite."""
        query = """
        INSERT INTO meeting_participants (meeting_id, user_id, response)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE response = %s, updated_at = NOW()
        """
        try:
            self.execute_query(query, (meeting_id, user_id, response, response), fetch=False)
            return True
        except Error:
            return False
    
    # Reporting
    def get_meeting_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics for meetings in a date range."""
        # Get basic counts
        query_counts = """
        SELECT 
            COUNT(*) as total_meetings,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
            SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled
        FROM meetings
        WHERE meeting_date BETWEEN %s AND %s
        """
        counts = self.execute_query(query_counts, (start_date, end_date))[0]
        
        # Get top organizers
        query_organizers = """
        SELECT 
            u.name as organizer,
            COUNT(*) as meetings_created,
            AVG(TIMESTAMPDIFF(MINUTE, ts.start_time, ts.end_time)) as avg_duration_minutes
        FROM meetings m
        JOIN users u ON m.created_by = u.user_id
        JOIN time_slots ts ON m.slot_id = ts.slot_id
        WHERE m.meeting_date BETWEEN %s AND %s
        GROUP BY u.user_id
        ORDER BY meetings_created DESC
        LIMIT 5
        """
        top_organizers = self.execute_query(query_organizers, (start_date, end_date))
        
        return {
            "period": {"start": start_date, "end": end_date},
            "counts": counts,
            "top_organizers": top_organizers
        }
    
    # Utility methods
    def check_room_availability(self, room_id: int, date: date, start_time: str, end_time: str) -> bool:
        """Check if a room is available for a specific time slot."""
        query = """
        SELECT COUNT(*) as count
        FROM meetings m
        JOIN time_slots ts ON m.slot_id = ts.slot_id
        WHERE m.room_id = %s
        AND m.meeting_date = %s
        AND m.status != 'cancelled'
        AND (
            (ts.start_time < %s AND ts.end_time > %s) OR
            (ts.start_time < %s AND ts.end_time > %s) OR
            (ts.start_time >= %s AND ts.end_time <= %s)
        )
        """
        result = self.execute_query(
            query, 
            (room_id, date, end_time, start_time, start_time, end_time, start_time, end_time)
        )
        return result[0]['count'] == 0
    
    def get_user_schedule(self, user_id: int, start_date: date, end_date: date) -> List[Dict]:
        """Get a user's schedule between two dates."""
        query = """
        SELECT 
            m.meeting_id,
            m.title,
            m.description,
            m.meeting_date,
            m.status,
            ts.start_time,
            ts.end_time,
            ts.day_of_week,
            mr.name as room_name,
            u.name as organizer_name,
            (SELECT COUNT(*) 
             FROM meeting_participants mp 
             WHERE mp.meeting_id = m.meeting_id 
             AND mp.response = 'accepted') as participant_count
        FROM meetings m
        JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
        JOIN users u ON m.created_by = u.user_id
        LEFT JOIN meeting_rooms mr ON m.room_id = mr.room_id
        JOIN time_slots ts ON m.slot_id = ts.slot_id
        WHERE mp.user_id = %s
        AND m.meeting_date BETWEEN %s AND %s
        AND m.status != 'cancelled'
        AND mp.response = 'accepted'
        ORDER BY m.meeting_date, ts.start_time
        """
        return self.execute_query(query, (user_id, start_date, end_date))

    def get_meeting_details_with_participants(self, meeting_id: int) -> Optional[Dict]:
        """Get detailed meeting information with nested participant data."""
        query = """
        SELECT 
            m.*,
            JSON_OBJECT(
                'name', u.name,
                'email', u.email,
                'role', u.role
            ) as organizer,
            JSON_OBJECT(
                'name', mr.name,
                'capacity', mr.capacity
            ) as room,
            JSON_OBJECT(
                'start_time', ts.start_time,
                'end_time', ts.end_time,
                'day_of_week', ts.day_of_week
            ) as time_slot,
            (
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'user_id', p.user_id,
                        'name', u2.name,
                        'email', u2.email,
                        'response', mp.response,
                        'response_date', mp.updated_at
                    )
                )
                FROM meeting_participants mp
                JOIN users u2 ON mp.user_id = u2.user_id
                WHERE mp.meeting_id = m.meeting_id
            ) as participants
        FROM meetings m
        JOIN users u ON m.created_by = u.user_id
        LEFT JOIN meeting_rooms mr ON m.room_id = mr.room_id
        JOIN time_slots ts ON m.slot_id = ts.slot_id
        WHERE m.meeting_id = %s
        """
        results = self.execute_complex_query(query, (meeting_id,), nested_results=True)
        return results[0] if results else None

    def get_user_schedule_with_conflicts(self, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get user schedule with potential scheduling conflicts."""
        query = """
        WITH user_meetings AS (
            SELECT 
                m.meeting_id,
                m.meeting_date,
                ts.start_time,
                ts.end_time,
                m.title,
                mr.name as room_name
            FROM meetings m
            JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
            JOIN time_slots ts ON m.slot_id = ts.slot_id
            LEFT JOIN meeting_rooms mr ON m.room_id = mr.room_id
            WHERE mp.user_id = %s 
            AND m.meeting_date BETWEEN %s AND %s
            AND m.status = 'scheduled'
            AND mp.response = 'accepted'
        ),
        conflicts AS (
            SELECT 
                m1.meeting_id as meeting1_id,
                m2.meeting_id as meeting2_id,
                m1.meeting_date,
                JSON_OBJECT(
                    'meeting1', JSON_OBJECT(
                        'id', m1.meeting_id,
                        'title', m1.title,
                        'start_time', m1.start_time,
                        'end_time', m1.end_time,
                        'room', m1.room_name
                    ),
                    'meeting2', JSON_OBJECT(
                        'id', m2.meeting_id,
                        'title', m2.title,
                        'start_time', m2.start_time,
                        'end_time', m2.end_time,
                        'room', m2.room_name
                    )
                ) as conflict_details
            FROM user_meetings m1
            JOIN user_meetings m2 ON m1.meeting_date = m2.meeting_date
            AND m1.meeting_id < m2.meeting_id
            AND (
                (m1.start_time < m2.end_time AND m1.end_time > m2.start_time)
                OR 
                (m2.start_time < m1.end_time AND m2.end_time > m1.start_time)
            )
        )
        SELECT 
            JSON_OBJECT(
                'schedule', JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'meeting_id', m.meeting_id,
                        'title', m.title,
                        'date', m.meeting_date,
                        'start_time', ts.start_time,
                        'end_time', ts.end_time,
                        'room', mr.name,
                        'participants', (
                            SELECT COUNT(*) 
                            FROM meeting_participants mp2 
                            WHERE mp2.meeting_id = m.meeting_id 
                            AND mp2.response = 'accepted'
                        )
                    )
                ),
                'conflicts', IFNULL(
                    (
                        SELECT JSON_ARRAYAGG(c.conflict_details)
                        FROM conflicts c
                    ),
                    JSON_ARRAY()
                )
            ) as result
        FROM meetings m
        JOIN meeting_participants mp ON m.meeting_id = mp.meeting_id
        JOIN time_slots ts ON m.slot_id = ts.slot_id
        LEFT JOIN meeting_rooms mr ON m.room_id = mr.room_id
        WHERE mp.user_id = %s
        AND m.meeting_date BETWEEN %s AND %s
        AND m.status = 'scheduled'
        AND mp.response = 'accepted'
        GROUP BY mp.user_id
        """
        results = self.execute_complex_query(query, (user_id, start_date, end_date, user_id, start_date, end_date), nested_results=True)
        return results[0] if results else {'schedule': [], 'conflicts': []}

    def search_meetings(self, search_params: Dict[str, Any]) -> List[Dict]:
        """
        Advanced meeting search with multiple criteria and nested results.
        
        Args:
            search_params: Dictionary containing search criteria:
                - title_keyword: str
                - date_range: tuple(date, date)
                - participant_id: int
                - room_id: int
                - status: str
                - organizer_id: int
        """
        conditions = []
        params = []
        
        base_query = """
        SELECT 
            m.*,
            JSON_OBJECT(
                'name', u.name,
                'email', u.email
            ) as organizer,
            JSON_OBJECT(
                'name', mr.name,
                'capacity', mr.capacity
            ) as room,
            JSON_OBJECT(
                'start_time', ts.start_time,
                'end_time', ts.end_time,
                'day_of_week', ts.day_of_week
            ) as time_slot,
            (
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'user_id', u2.user_id,
                        'name', u2.name,
                        'response', mp.response
                    )
                )
                FROM meeting_participants mp
                JOIN users u2 ON mp.user_id = u2.user_id
                WHERE mp.meeting_id = m.meeting_id
            ) as participants
        FROM meetings m
        JOIN users u ON m.created_by = u.user_id
        LEFT JOIN meeting_rooms mr ON m.room_id = mr.room_id
        JOIN time_slots ts ON m.slot_id = ts.slot_id
        """
        
        if 'title_keyword' in search_params and search_params['title_keyword']:
            conditions.append("m.title LIKE %s")
            params.append(f"%{search_params['title_keyword']}%")
        
        if 'date_range' in search_params and search_params['date_range']:
            start_date, end_date = search_params['date_range']
            conditions.append("m.meeting_date BETWEEN %s AND %s")
            params.extend([start_date, end_date])
        
        if 'participant_id' in search_params and search_params['participant_id']:
            base_query += " JOIN meeting_participants mp2 ON m.meeting_id = mp2.meeting_id"
            conditions.append("mp2.user_id = %s")
            params.append(search_params['participant_id'])
        
        if 'room_id' in search_params and search_params['room_id']:
            conditions.append("m.room_id = %s")
            params.append(search_params['room_id'])
        
        if 'status' in search_params and search_params['status']:
            conditions.append("m.status = %s")
            params.append(search_params['status'])
        
        if 'organizer_id' in search_params and search_params['organizer_id']:
            conditions.append("m.created_by = %s")
            params.append(search_params['organizer_id'])
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY m.meeting_date, ts.start_time"
        
        return self.execute_complex_query(base_query, tuple(params), nested_results=True)

# Singleton instance
db = Database()
