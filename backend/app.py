from flask import Flask, request, jsonify
from datetime import datetime, date
from database import db
from auth import generate_token, verify_token, token_required, role_required, AuthError
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ============================================
# Authentication Endpoints
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user by email and role, return JWT token."""
    data = request.get_json()
    try:
        email = data.get('email')
        role = data.get('role')
        
        if not email or not role:
            return jsonify({
                'status': 'error',
                'message': 'Email and role are required'
            }), 400
        
        user = db.get_user(email=email)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        if user['role'] != role:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role for this user'
            }), 400
        
        # Generate JWT token
        token = generate_token(user['user_id'], user['email'], user['role'])
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'token': token
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user and return JWT token."""
    data = request.get_json()
    try:
        user_id = db.create_user(
            name=data.get('name', data.get('email', 'User')),
            email=data['email'],
            role=data.get('role', 'student')
        )
        
        # Generate JWT token for newly registered user
        token = generate_token(user_id, data['email'], data.get('role', 'student'))
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'user_id': user_id,
                'email': data['email'],
                'role': data.get('role', 'student'),
                'token': token
            }
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/auth/verify', methods=['POST'])
def verify_auth():
    """Verify if a token is valid."""
    data = request.get_json()
    try:
        token = data.get('token')
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token is required'
            }), 400
        
        payload = verify_token(token)
        return jsonify({
            'status': 'success',
            'data': {
                'valid': True,
                'user_id': payload['user_id'],
                'email': payload['email'],
                'role': payload['role']
            }
        }), 200
    except AuthError as e:
        return jsonify({
            'status': 'error',
            'message': e.error,
            'data': {'valid': False}
        }), e.status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ============================================
# User Endpoints
# ============================================

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details."""
    try:
        user = db.get_user(user_id=user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': user
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user."""
    data = request.get_json()
    try:
        user_id = db.create_user(
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'student')
        )
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'user_id': user_id
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ============================================
# Meeting Endpoints
# ============================================

@app.route('/api/meetings', methods=['POST'])
def create_meeting():
    """Create a new meeting."""
    data = request.get_json()
    try:
        meeting_id = db.create_meeting(
            title=data['title'],
            description=data.get('description', ''),
            room_id=data.get('room_id'),
            slot_id=data['slot_id'],
            meeting_date=datetime.strptime(data['meeting_date'], '%Y-%m-%d').date(),
            created_by=data['created_by'],
            participants=data.get('participants', [])
        )
        return jsonify({
            'status': 'success',
            'message': 'Meeting created successfully',
            'meeting_id': meeting_id
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/meetings/<int:meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    """Get meeting details with participants."""
    try:
        meeting = db.get_meeting_details_with_participants(meeting_id)
        if not meeting:
            return jsonify({
                'status': 'error',
                'message': 'Meeting not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': meeting
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/meetings/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    """Delete/Cancel a meeting."""
    try:
        query = "UPDATE meetings SET status = 'cancelled' WHERE meeting_id = %s"
        db.execute_query(query, (meeting_id,), fetch=False)
        return jsonify({
            'status': 'success',
            'message': 'Meeting cancelled successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/meetings/upcoming', methods=['GET'])
def get_upcoming_meetings():
    """Get upcoming meetings for a user."""
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 10))
    
    try:
        meetings = db.get_upcoming_meetings(
            user_id=int(user_id) if user_id else None,
            limit=limit
        )
        return jsonify({
            'status': 'success',
            'data': meetings
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/meetings/search', methods=['POST'])
def search_meetings():
    """Search meetings with complex filters."""
    data = request.get_json()
    try:
        search_params = {
            'title_keyword': data.get('title_keyword'),
            'date_range': tuple(data.get('date_range', [])) if data.get('date_range') else None,
            'participant_id': data.get('participant_id'),
            'room_id': data.get('room_id'),
            'status': data.get('status'),
            'organizer_id': data.get('organizer_id')
        }
        
        meetings = db.search_meetings(search_params)
        return jsonify({
            'status': 'success',
            'data': meetings
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/user/<int:user_id>/schedule', methods=['GET'])
def get_user_schedule(user_id):
    """Get user's schedule with conflict detection."""
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else date.today()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else start_date
        
        schedule = db.get_user_schedule_with_conflicts(user_id, start_date, end_date)
        return jsonify({
            'status': 'success',
            'data': schedule
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ============================================
# Room Endpoints
# ============================================

@app.route('/api/rooms', methods=['GET'])
def get_all_rooms():
    """Get all meeting rooms."""
    try:
        query = "SELECT * FROM meeting_rooms WHERE is_active = TRUE"
        rooms = db.execute_query(query)
        return jsonify({
            'status': 'success',
            'data': rooms
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/rooms/available', methods=['GET'])
def get_available_rooms():
    """Get available rooms for a time slot."""
    date_str = request.args.get('date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    try:
        rooms = db.get_available_rooms(
            date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            start_time=start_time,
            end_time=end_time
        )
        return jsonify({
            'status': 'success',
            'data': rooms
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ============================================
# Time Slot Endpoints
# ============================================

@app.route('/api/timeslots', methods=['GET'])
def get_time_slots():
    """Get all available time slots."""
    try:
        query = "SELECT * FROM time_slots ORDER BY start_time"
        slots = db.execute_query(query)
        return jsonify({
            'status': 'success',
            'data': slots
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/timeslots/available', methods=['GET'])
def get_available_timeslots():
    """Get available time slots for a user on a specific date."""
    user_id = request.args.get('user_id')
    date_str = request.args.get('date')
    
    try:
        available = db.get_available_time_slots(
            user_id=int(user_id),
            date=datetime.strptime(date_str, '%Y-%m-%d').date()
        )
        return jsonify({
            'status': 'success',
            'data': available
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ============================================
# Participant Endpoints
# ============================================

@app.route('/api/meetings/<int:meeting_id>/respond', methods=['POST'])
def respond_to_meeting(meeting_id):
    """Respond to a meeting invitation."""
    data = request.get_json()
    try:
        success = db.update_participant_response(
            meeting_id=meeting_id,
            user_id=data['user_id'],
            response=data['response']
        )
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Response recorded successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to record response'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ============================================
# Analytics Endpoints
# ============================================

@app.route('/api/analytics/meetings', methods=['GET'])
def get_meeting_analytics():
    """Get meeting analytics for a date range."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date', str(date.today()))
    
    try:
        analytics = db.get_meeting_analytics(
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date()
        )
        return jsonify({
            'status': 'success',
            'data': analytics
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ============================================
# Health Check
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'success',
        'message': 'API is running'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Home endpoint."""
    return jsonify({
        'status': 'success',
        'message': 'Academic Meeting Scheduler API',
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
