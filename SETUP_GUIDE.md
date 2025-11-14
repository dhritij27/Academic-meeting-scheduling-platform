# Academic Meeting Scheduler - Setup & Testing Guide

## 📋 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
- No additional dependencies needed for vanilla JavaScript. Just open `index.html` in a browser.

### 2. Setup Database

**Option A: Using Docker (Recommended)**
```bash
docker run --name mysql-meeting -e MYSQL_ROOT_PASSWORD=password -d -p 3306:3306 mysql:8.0
```

**Option B: Direct MySQL Installation**
Make sure MySQL is running on localhost:3306

### 3. Configure Environment

Create/Edit `.env` file in the `backend/` directory:
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=academic_meetings
MYSQL_USER=root
MYSQL_PASSWORD=password
PORT=5000
```

### 4. Initialize Database Schema

Run the schema SQL file:
```bash
mysql -u root -p < backend/schema.sql
```

### 5. Seed Fake Data

```bash
python backend/seed_data.py
```

Expected output:
```
==================================================
Database Seeding Started
==================================================

1. Clearing existing data...
✓ Cleared meeting_participants
✓ Cleared meetings
✓ Cleared user_availability
✓ Cleared time_slots
✓ Cleared meeting_rooms
✓ Cleared users

2. Seeding users...
  ✓ Created user: Alice Johnson (student)
  ... (more users)
✓ Created 14 users

3. Seeding meeting rooms...
  ✓ Created room: Conference Room A
  ... (more rooms)
✓ Created 8 rooms

4. Seeding time slots...
✓ Created/Retrieved 25 time slots

5. Seeding user availability...
✓ Created 69 availability records

6. Seeding meetings...
✓ Created 14 meetings

7. Seeding meeting participants...
✓ Added 41 meeting participants

==================================================
✓ Database Seeding Completed Successfully!
==================================================

Summary:
  • Users: 14
  • Rooms: 8
  • Time Slots: 25
  • Meetings: 14
==================================================
```

### 6. Start Backend Server

```bash
python backend/app.py
```

Server will run on `http://localhost:5000`

### 7. Start Frontend

Open `index.html` in a browser or serve via a local server:
```bash
# Option 1: Python 3
python -m http.server 8000

# Option 2: Node.js (if installed)
npx http-server

# Option 3: VS Code Live Server extension
# Right-click index.html → Open with Live Server
```

Frontend will be at `http://localhost:8000` or `http://localhost:5500` (Live Server)

---

## 🔐 Login Credentials (After Seeding)

Use the following emails with any password to login (password validation is currently disabled):

**Students:**
- `alice@university.edu` (student)
- `bob@university.edu` (student)
- `charlie@university.edu` (student)
- `diana@university.edu` (student)
- `evan@university.edu` (student)

**Professors/FAMs:**
- `rajesh.kumar@university.edu` (professor)
- `priya.sharma@university.edu` (professor)
- `ishaan.gupta@university.edu` (professor)
- `tanvi.das@university.edu` (professor)

---

## 🧪 Testing CRUD Operations

### Create Operations

**Create a New Meeting:**
```bash
curl -X POST http://localhost:5000/api/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project Discussion",
    "description": "Discussing final project",
    "room_id": 1,
    "slot_id": 1,
    "meeting_date": "2025-11-20",
    "created_by": 1,
    "participants": [2, 3, 4]
  }'
```

**Create a New User:**
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@university.edu",
    "role": "student"
  }'
```

### Read Operations

**Get Upcoming Meetings for User:**
```bash
curl "http://localhost:5000/api/meetings/upcoming?user_id=1&limit=10"
```

**Get All Meeting Rooms:**
```bash
curl "http://localhost:5000/api/rooms"
```

**Get Time Slots:**
```bash
curl "http://localhost:5000/api/timeslots"
```

**Get Meeting Details:**
```bash
curl "http://localhost:5000/api/meetings/1"
```

**Search Meetings:**
```bash
curl -X POST http://localhost:5000/api/meetings/search \
  -H "Content-Type: application/json" \
  -d '{
    "title_keyword": "Project",
    "status": "scheduled"
  }'
```

### Update Operations

**Respond to Meeting Invitation:**
```bash
curl -X POST http://localhost:5000/api/meetings/1/respond \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "response": "accepted"
  }'
```

### Delete Operations

**Cancel a Meeting:**
```bash
curl -X DELETE http://localhost:5000/api/meetings/1
```

---

## 📊 Advanced Query Examples

### Find Available Time Slots for User
```bash
curl "http://localhost:5000/api/timeslots/available?user_id=1&date=2025-11-15"
```

### Get Available Rooms for Date & Time
```bash
curl "http://localhost:5000/api/rooms/available?date=2025-11-15&start_time=10:00&end_time=11:00"
```

### Get User Schedule with Conflicts
```bash
curl "http://localhost:5000/api/user/1/schedule?start_date=2025-11-10&end_date=2025-11-20"
```

### Get Meeting Analytics
```bash
curl "http://localhost:5000/api/analytics/meetings?start_date=2025-11-01&end_date=2025-11-30"
```

---

## 🛠️ Frontend Features

### Student Features:
- ✅ View upcoming meetings
- ✅ View personal availability
- ✅ View available FAMs (First-year Academic Mentors)
- ✅ Book meetings with FAMs or professors
- ✅ Accept/decline meeting invitations
- ✅ Respond to meeting participations

### Professor Features:
- ✅ View assigned meetings
- ✅ View student schedules
- ✅ Manage meeting participants
- ✅ View analytics

### FAM Features:
- ✅ View scheduled meetings
- ✅ Add notes to student meetings
- ✅ Track mentee progress
- ✅ Manage availability

---

## 🗄️ Database Structure

### Tables:
1. **users** - All system users (students, professors, FAMs)
2. **meetings** - Scheduled meetings
3. **meeting_participants** - Meeting attendees and their responses
4. **meeting_rooms** - Available physical spaces
5. **time_slots** - Recurring time slots
6. **user_availability** - When each user is available

### Sample Data:
- **14 Users** (5 students, 4 professors, 5 FAMs)
- **8 Meeting Rooms**
- **25 Time Slots** (Mon-Fri, 9-5 schedule)
- **14 Meetings** (spread across next 14 days)
- **40+ Meeting Participations**

---

## 🐛 Troubleshooting

### Issue: "Connection refused" on Port 5000
**Solution:** Backend server not running
```bash
python backend/app.py
```

### Issue: "Connection refused" on Port 3306
**Solution:** MySQL not running
```bash
# Start MySQL service
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql
# Windows: net start MySQL80
```

### Issue: "No module named 'flask'"
**Solution:** Install requirements
```bash
pip install -r backend/requirements.txt
```

### Issue: "Authentication Plugin 'caching_sha2_password' cannot be loaded"
**Solution:** Use MySQL 5.7 or earlier, or update Python MySQL connector:
```bash
pip install --upgrade mysql-connector-python
```

### Issue: Frontend not connecting to backend
**Solution:** Make sure CORS is enabled (already configured in app.py)

---

## 📝 API Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/register` | User registration |
| GET | `/api/users/<id>` | Get user details |
| POST | `/api/users` | Create new user |
| GET | `/api/meetings/upcoming` | Get upcoming meetings |
| POST | `/api/meetings` | Create meeting |
| GET | `/api/meetings/<id>` | Get meeting details |
| DELETE | `/api/meetings/<id>` | Cancel meeting |
| POST | `/api/meetings/search` | Search meetings |
| POST | `/api/meetings/<id>/respond` | Respond to invitation |
| GET | `/api/rooms` | Get all rooms |
| GET | `/api/rooms/available` | Get available rooms |
| GET | `/api/timeslots` | Get all time slots |
| GET | `/api/timeslots/available` | Get user's available slots |
| GET | `/api/user/<id>/schedule` | Get user schedule |
| GET | `/api/analytics/meetings` | Get meeting analytics |

---

## ✨ Features Implemented

### Backend Enhancements:
- ✅ Complex nested queries with JSON aggregation
- ✅ Conflict detection algorithm
- ✅ Advanced search with multiple filters
- ✅ Analytics and reporting
- ✅ Query optimization for large datasets
- ✅ Connection pooling for performance

### Frontend Integration:
- ✅ Real-time meeting status updates
- ✅ Role-based access control
- ✅ Responsive UI design
- ✅ Error handling and validation
- ✅ User authentication flow

---

## 📚 Next Steps

1. **Customize Styling**: Edit `style.css` for your institution's branding
2. **Add Email Notifications**: Integrate email service for meeting reminders
3. **Implement Real-time Updates**: Add WebSocket support for live notifications
4. **Add Calendar Integration**: Sync with Google Calendar or Outlook
5. **Mobile App**: Build React Native or Flutter mobile version

---

## 📞 Support

For issues or questions, refer to:
- Database logs: `backend/server.log`
- API documentation: Endpoints listed above
- Sample data: `backend/seed_data.py`

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.
