# 📚 API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## 🔐 Authentication Endpoints

### 1. Login
**POST** `/auth/login`

Login a user and receive a JWT token.

**Request:**
```json
{
  "email": "alice@university.edu",
  "role": "student"
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "user_id": 1,
    "name": "Alice Johnson",
    "email": "alice@university.edu",
    "role": "student",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Error Response (404):**
```json
{
  "status": "error",
  "message": "User not found"
}
```

---

### 2. Register
**POST** `/auth/register`

Register a new user and receive a JWT token.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@university.edu",
  "role": "student"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "user_id": 15,
    "email": "john@university.edu",
    "role": "student",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### 3. Verify Token
**POST** `/auth/verify`

Verify if a JWT token is still valid.

**Request:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "valid": true,
    "user_id": 1,
    "email": "alice@university.edu",
    "role": "student"
  }
}
```

**Error Response (401):**
```json
{
  "status": "error",
  "message": "Token has expired",
  "data": {
    "valid": false
  }
}
```

---

## 👥 User Endpoints

### 1. Get User by ID
**GET** `/users/<user_id>`

Get details of a specific user.

**Parameters:**
- `user_id` (path): User ID

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "user_id": 1,
    "name": "Alice Johnson",
    "email": "alice@university.edu",
    "role": "student",
    "created_at": "2025-11-12T10:30:00",
    "updated_at": "2025-11-12T10:30:00"
  }
}
```

---

### 2. Create User
**POST** `/users`

Create a new user.

**Request:**
```json
{
  "name": "Jane Smith",
  "email": "jane@university.edu",
  "role": "professor"
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "User created successfully",
  "user_id": 16
}
```

---

## 📅 Meeting Endpoints

### 1. Create Meeting
**POST** `/meetings`

Create a new meeting.

**Request:**
```json
{
  "title": "Data Structures Discussion",
  "description": "Discussing advanced DS concepts",
  "room_id": 1,
  "slot_id": 1,
  "meeting_date": "2025-11-20",
  "created_by": 1,
  "participants": [2, 3, 4]
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Meeting created successfully",
  "meeting_id": 15
}
```

---

### 2. Get Meeting Details
**GET** `/meetings/<meeting_id>`

Get detailed information about a specific meeting including participants.

**Parameters:**
- `meeting_id` (path): Meeting ID

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "meeting_id": 1,
    "title": "Data Structures Discussion",
    "description": "Discussing advanced DS concepts",
    "meeting_date": "2025-11-20",
    "status": "scheduled",
    "organizer": {
      "name": "Alice Johnson",
      "email": "alice@university.edu",
      "role": "student"
    },
    "room": {
      "name": "Conference Room A",
      "capacity": 10
    },
    "time_slot": {
      "start_time": "10:00",
      "end_time": "11:00",
      "day_of_week": "monday"
    },
    "participants": [
      {
        "user_id": 2,
        "name": "Bob Smith",
        "email": "bob@university.edu",
        "response": "accepted",
        "response_date": "2025-11-15T14:30:00"
      }
    ]
  }
}
```

---

### 3. Get Upcoming Meetings
**GET** `/meetings/upcoming`

Get upcoming meetings for a user.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `limit` (optional, default: 10): Number of meetings to return

**Example:**
```
GET /meetings/upcoming?user_id=1&limit=5
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "meeting_id": 1,
      "title": "Meeting Title",
      "meeting_date": "2025-11-20",
      "status": "scheduled",
      "organizer_name": "Alice Johnson",
      "room_name": "Conference Room A",
      "start_time": "10:00",
      "end_time": "11:00"
    }
  ]
}
```

---

### 4. Search Meetings
**POST** `/meetings/search`

Search for meetings with advanced filters.

**Request:**
```json
{
  "title_keyword": "Discussion",
  "date_range": ["2025-11-01", "2025-11-30"],
  "participant_id": 2,
  "room_id": 1,
  "status": "scheduled",
  "organizer_id": 1
}
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "meeting_id": 1,
      "title": "Data Structures Discussion",
      "meeting_date": "2025-11-20",
      "organizer": {
        "name": "Alice Johnson",
        "email": "alice@university.edu"
      },
      "participants": [...]
    }
  ]
}
```

---

### 5. Cancel Meeting
**DELETE** `/meetings/<meeting_id>`

Cancel a meeting (changes status to 'cancelled').

**Parameters:**
- `meeting_id` (path): Meeting ID

**Response (200):**
```json
{
  "status": "success",
  "message": "Meeting cancelled successfully"
}
```

---

## 🏢 Room Endpoints

### 1. Get All Rooms
**GET** `/rooms`

Get all active meeting rooms.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "room_id": 1,
      "name": "Conference Room A",
      "capacity": 10,
      "is_active": true,
      "created_at": "2025-11-12T10:00:00"
    }
  ]
}
```

---

### 2. Get Available Rooms
**GET** `/rooms/available`

Get available rooms for a specific date and time.

**Query Parameters:**
- `date` (required): Date in YYYY-MM-DD format
- `start_time` (required): Start time in HH:MM format
- `end_time` (required): End time in HH:MM format

**Example:**
```
GET /rooms/available?date=2025-11-20&start_time=10:00&end_time=11:00
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "room_id": 1,
      "name": "Conference Room A",
      "capacity": 10,
      "is_active": true
    },
    {
      "room_id": 2,
      "name": "Conference Room B",
      "capacity": 8,
      "is_active": true
    }
  ]
}
```

---

## ⏰ Time Slot Endpoints

### 1. Get All Time Slots
**GET** `/timeslots`

Get all available time slots.

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "slot_id": 1,
      "start_time": "09:00",
      "end_time": "10:00",
      "day_of_week": "monday",
      "is_recurring": true,
      "created_at": "2025-11-12T10:00:00"
    }
  ]
}
```

---

### 2. Get User's Available Time Slots
**GET** `/timeslots/available`

Get available time slots for a user on a specific date.

**Query Parameters:**
- `user_id` (required): User ID
- `date` (required): Date in YYYY-MM-DD format

**Example:**
```
GET /timeslots/available?user_id=1&date=2025-11-20
```

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "slot_id": 1,
      "start_time": "10:00",
      "end_time": "11:00",
      "day_of_week": "wednesday",
      "is_recurring": true
    }
  ]
}
```

---

## 👥 Participant Endpoints

### 1. Respond to Meeting Invitation
**POST** `/meetings/<meeting_id>/respond`

Accept, decline, or mark as pending a meeting invitation.

**Parameters:**
- `meeting_id` (path): Meeting ID

**Request:**
```json
{
  "user_id": 2,
  "response": "accepted"
}
```

**Valid Responses:** `accepted`, `declined`, `pending`

**Response (200):**
```json
{
  "status": "success",
  "message": "Response recorded successfully"
}
```

---

## 📊 Schedule & Analytics Endpoints

### 1. Get User Schedule
**GET** `/user/<user_id>/schedule`

Get user's schedule with conflict detection.

**Parameters:**
- `user_id` (path): User ID
- `start_date` (query, optional): Start date in YYYY-MM-DD format
- `end_date` (query, optional): End date in YYYY-MM-DD format

**Example:**
```
GET /user/1/schedule?start_date=2025-11-10&end_date=2025-11-20
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "schedule": [
      {
        "meeting_id": 1,
        "title": "Meeting Title",
        "date": "2025-11-15",
        "start_time": "10:00",
        "end_time": "11:00",
        "room": "Conference Room A",
        "participants": 3
      }
    ],
    "conflicts": []
  }
}
```

---

### 2. Get Meeting Analytics
**GET** `/analytics/meetings`

Get analytics for meetings in a date range.

**Query Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (optional, default: today): End date in YYYY-MM-DD format

**Example:**
```
GET /analytics/meetings?start_date=2025-10-01&end_date=2025-11-30
```

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "period": {
      "start": "2025-10-01",
      "end": "2025-11-30"
    },
    "counts": {
      "total_meetings": 14,
      "completed": 2,
      "cancelled": 0,
      "scheduled": 12
    },
    "top_organizers": [
      {
        "organizer": "Alice Johnson",
        "meetings_created": 5,
        "avg_duration_minutes": 60.0,
        "avg_participants_per_meeting": 2.5
      }
    ]
  }
}
```

---

## ❌ Error Responses

### 400 - Bad Request
Missing or invalid parameters
```json
{
  "status": "error",
  "message": "Email and role are required",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 - Unauthorized
Missing or invalid token
```json
{
  "status": "error",
  "message": "Token has expired"
}
```

### 403 - Forbidden
Insufficient permissions
```json
{
  "status": "error",
  "message": "Insufficient permissions. Required roles: admin"
}
```

### 404 - Not Found
Resource not found
```json
{
  "status": "error",
  "message": "User not found"
}
```

### 500 - Internal Server Error
Server error
```json
{
  "status": "error",
  "message": "An internal server error occurred"
}
```

---

## 🔄 Common Workflows

### Workflow 1: Schedule a Meeting
1. Login: `POST /auth/login`
2. Get available rooms: `GET /rooms/available`
3. Get available time slots: `GET /timeslots/available`
4. Create meeting: `POST /meetings`
5. Add participants: POST to `/meetings/<id>/respond`

### Workflow 2: View Schedule
1. Login: `POST /auth/login`
2. Get user schedule: `GET /user/<id>/schedule`
3. View meeting details: `GET /meetings/<id>`

### Workflow 3: Accept Meeting Invitation
1. Login: `POST /auth/login`
2. Get upcoming meetings: `GET /meetings/upcoming`
3. Respond to invitation: `POST /meetings/<id>/respond`

---

## 🚀 Rate Limiting
Currently not implemented. Consider adding rate limiting for production.

## 📋 Pagination
Not implemented yet. All list endpoints return all results.

---

**Last Updated:** November 12, 2025
