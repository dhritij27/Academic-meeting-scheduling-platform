import os
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import date, datetime, time
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling, Error
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor, MySQLCursorDict

# Load environment variables from .env if present
load_dotenv()

class MySQLPool:
    _pool: Optional[pooling.MySQLConnectionPool] = None

    @classmethod
    def init_pool(cls):
        if cls._pool is not None:
            return cls._pool
        db_config = {
            "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", ""),
            "database": os.getenv("MYSQL_DATABASE", "academic_meetings"),
            "raise_on_warnings": True
        }
        cls._pool = pooling.MySQLConnectionPool(
            pool_name="academic_pool",
            pool_size=int(os.getenv("MYSQL_POOL_SIZE", "5")),
            **db_config,
        )
        return cls._pool

    @classmethod
    def get_conn(cls) -> MySQLConnection:
        if cls._pool is None:
            cls.init_pool()
        return cls._pool.get_connection()


def ping_db() -> bool:
    """Check if the database connection is working."""
    conn = None
    try:
        conn = MySQLPool.get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return True
    except Exception as e:
        print(f"Database ping failed: {e}")
        return False
    finally:
        if conn:
            conn.close()


def execute_query(query: str, params: tuple = None, fetch: bool = True, multi: bool = False) -> Union[MySQLCursor, List[Dict[str, Any]]]:
    """
    Execute a SQL query and return the results.
    
    Args:
        query: SQL query to execute
        params: Parameters for the query
        fetch: Whether to fetch and return results
        multi: Whether to execute multiple statements
    
    Returns:
        List of dictionaries (for SELECT) or cursor (for other operations)
    """
    conn = None
    cursor = None
    try:
        conn = MySQLPool.get_conn()
        cursor = conn.cursor(dictionary=True)
        
        if multi:
            for result in cursor.execute(query, params, multi=True):
                if result.with_rows:
                    result.fetchall()
            conn.commit()
            return cursor
        else:
            cursor.execute(query, params or ())
            if fetch and cursor.with_rows:
                result = cursor.fetchall()
                return result
            conn.commit()
            return cursor
            
    except Error as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_procedure(proc_name: str, args: tuple = None) -> List[Dict[str, Any]]:
    """
    Execute a stored procedure and return the results.
    
    Args:
        proc_name: Name of the stored procedure
        args: Arguments to pass to the procedure
    """
    conn = None
    cursor = None
    try:
        conn = MySQLPool.get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Convert date and time objects to strings for MySQL
        if args:
            processed_args = []
            for arg in args:
                if isinstance(arg, (date, datetime)):
                    processed_args.append(arg.strftime('%Y-%m-%d'))
                elif isinstance(arg, time):
                    processed_args.append(arg.strftime('%H:%M:%S'))
                else:
                    processed_args.append(arg)
            args = tuple(processed_args)
        
        cursor.callproc(proc_name, args or ())
        results = []
        
        # Get all result sets
        for result in cursor.stored_results():
            results.extend(result.fetchall())
            
        return results
    except Error as e:
        print(f"Procedure error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_user_free_slots(user_id: int, target_date: date) -> List[Dict[str, Any]]:
    """
    Get a user's free time slots for a specific date.
    
    Args:
        user_id: ID of the user
        target_date: Date to check availability for
        
    Returns:
        List of dictionaries with slot information
    """
    try:
        # Call the stored procedure
        results = execute_procedure('get_user_free_slots', (user_id, target_date))
        return results
    except Error as e:
        print(f"Error getting free slots: {e}")
        return []


def get_available_rooms(slot_id: int, meeting_date: date) -> List[Dict[str, Any]]:
    """
    Get available rooms for a specific time slot and date.
    
    Args:
        slot_id: ID of the time slot
        meeting_date: Date of the meeting
        
    Returns:
        List of available rooms
    """
    try:
        results = execute_procedure('get_available_rooms', (slot_id, meeting_date))
        return results
    except Error as e:
        print(f"Error getting available rooms: {e}")
        return []


def schedule_meeting(
    title: str,
    description: str,
    room_id: int,
    slot_id: int,
    meeting_date: date,
    created_by: int,
    participant_ids: List[int]
) -> int:
    """
    Schedule a new meeting and add participants.
    
    Args:
        title: Meeting title
        description: Meeting description
        room_id: ID of the meeting room
        slot_id: ID of the time slot
        meeting_date: Date of the meeting
        created_by: User ID of the meeting creator
        participant_ids: List of user IDs to invite
        
    Returns:
        ID of the created meeting
    """
    conn = None
    cursor = None
    try:
        conn = MySQLPool.get_conn()
        cursor = conn.cursor(dictionary=True)
        
        # Start transaction
        conn.start_transaction()
        
        # Insert the meeting
        cursor.execute("""
            INSERT INTO meetings (title, description, room_id, slot_id, meeting_date, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, room_id, slot_id, meeting_date, created_by))
        
        meeting_id = cursor.lastrowid
        
        # Add participants
        for user_id in set(participant_ids + [created_by]):  # Include creator as participant
            cursor.execute("""
                INSERT INTO meeting_participants (meeting_id, user_id, response)
                VALUES (%s, %s, 'accepted')
            """, (meeting_id, user_id))
        
        # Commit transaction
        conn.commit()
        return meeting_id
        
    except Error as e:
        if conn:
            conn.rollback()
        print(f"Error scheduling meeting: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_daily_schedule(target_date: date = None) -> List[Dict[str, Any]]:
    """
    Get the daily schedule of meetings.
    
    Args:
        target_date: Date to get schedule for (defaults to today)
        
    Returns:
        List of scheduled meetings
    """
    if target_date is None:
        target_date = date.today()
        
    try:
        query = """
            SELECT * FROM daily_schedule 
            WHERE meeting_date = %s
            ORDER BY start_time
        """
        results = execute_query(query, (target_date,))
        return results
    except Error as e:
        print(f"Error getting daily schedule: {e}")
        return []


def is_room_available(room_id: int, slot_id: int, meeting_date: date) -> bool:
    """
    Check if a room is available for a specific time slot and date.
    
    Args:
        room_id: ID of the room
        slot_id: ID of the time slot
        meeting_date: Date to check
        
    Returns:
        True if room is available, False otherwise
    """
    try:
        cursor = execute_query(
            "SELECT is_room_available(%s, %s, %s) AS is_available",
            (room_id, slot_id, meeting_date)
        )
        result = cursor.fetchone()
        return bool(result['is_available']) if result else False
    except Error as e:
        print(f"Error checking room availability: {e}")
        return False
