# Academic Meeting Scheduler 📅

A comprehensive web-based platform designed to facilitate seamless communication and mentorship within academic institutions. The platform bridges three critical types of academic interactions: student-professor consultations, peer mentorship through the FAM (First-year Academic Mentor) program, and peer-to-peer collaborative study sessions.

## Features

### Multi-Tier Meeting System
- **Student-Professor Meetings**: Book appointments for doubt clarification, project discussions, career guidance
- **Student-FAM Meetings**: Connect with assigned mentors for academic help and college life advice
- **Peer-to-Peer Meetings**: Schedule collaborative study sessions and project work

### Dynamic Availability Management
- Weekly recurring availability slots
- Real-time conflict detection
- Smart slot-matching algorithm
- Support for both online (video calls) and offline (in-person) meetings

### FAM Program Features
- Senior students as mentors with specializations
- Profile with bio, rating, and mentee capacity
- Rating and feedback system
- Mentor-mentee assignment tracking

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: MySQL
- **Backend**: Python (Flask), MySQL connector, dotenv
- **Icons**: Lucide Icons
- **Design**: Responsive, Mobile-First Design

## 📁 Project Structure

```
academic-meeting-scheduler/
├── README.md
├── database/
│   └── schema.sql
├── src/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── app.js
│   │   ├── data.js
│   │   └── utils.js
│   └── assets/
│       └── (images, icons, etc.)
└── docs/
    └── API_DOCUMENTATION.md
```

## Getting Started

### Prerequisites
- MySQL Server (5.7 or higher)
- Python 3.10+
- Web Browser (Chrome, Firefox, Safari, Edge)
- Text Editor (VS Code recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/academic-meeting-scheduler.git
   cd academic-meeting-scheduler
   ```

2. **Set up the database**
   ```bash
   # Login to MySQL
   mysql -u root -p

   # Create database
   CREATE DATABASE academic_meetings;
   USE academic_meetings;

   # Import schema
   source database/schema.sql
   ```

3. **Backend (Flask) setup**
   ```bash
   # From repo root
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your MySQL credentials
   # Start backend
   python backend/server.py
   ```

4. **Configure database connection**
   - Use `.env` variables (see `.env.example`): `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`

5. **Run the application (frontend)**
   - Open `index.html` in your browser
   - Or use a local development server:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js http-server
   npx http-server .
   ```

6. **Access the application**
   - Open browser: `http://localhost:8000`

---

## Backend Endpoints (initial)

- `GET /health` → health check for the Flask server
- `GET /db/ping` → tests DB connectivity using the configured pool

You can extend `backend/server.py` to add CRUD routes for meetings, availability, professors, students, and FAMs. See `database-schema.sql` for table ideas.

---

## Supabase Removal

- Supabase scripts and data layer have been removed from `index.html` and `login.html`.
- Files safe to delete if no longer needed:
  - `supabase-config.js`
  - `supabase-data.js`
  - `migrate-to-supabase.js`
  - `SUPABASE_SETUP.md`
  
Frontend currently uses `data.js` (local demo data). Replace these simulated functions by wiring API calls to your Flask endpoints as they are added.

## Usage Guide

### For Students
1. **Login** with your SRN and credentials
2. **View Dashboard** to see upcoming meetings
3. **Book Meeting**:
   - Select meeting type (Professor/FAM/Peer)
   - Choose the person
   - Pick available time slot
   - Add meeting purpose
4. **Manage Availability**: Update your free slots weekly

### For Professors
1. **Set Office Hours**: Define weekly availability
2. **View Appointments**: See all scheduled meetings
3. **Add Notes**: Document meeting outcomes

### For FAMs (Mentors)
1. **Set Mentoring Hours**: Define availability for mentees
2. **View Mentees**: Track assigned first-year students
3. **Manage Sessions**: Schedule and complete mentoring sessions

## Database Schema

### Main Tables
- `Students`: Student information and profiles
- `Professors`: Faculty information and departments
- `FAM`: First-year Academic Mentor profiles
- `Meetings`: All scheduled meetings
- `Student_Availability`: Student free time slots
- `Professor_Availability`: Professor office hours
- `FAM_Availability`: Mentor availability
- `FAM_Mentees`: Mentor-mentee relationships

### Key Relationships
- Students ↔ Meetings (1:Many)
- Professors ↔ Meetings (1:Many)
- FAM ↔ Students (Many:Many through FAM_Mentees)
- Meetings support three categories: Student-Professor, Student-FAM, Peer-to-Peer

## Customization

### Styling
- Modify `css/styles.css` for design changes
- Color scheme variables at top of CSS file
- Responsive breakpoints for mobile/tablet

### Data
- Sample data in `js/data.js`
- Connect to real backend by updating API endpoints
- Modify data structures as needed

## Security Considerations

When deploying to production:
- Implement proper authentication (JWT, OAuth)
- Add HTTPS/SSL encryption
- Sanitize all user inputs
- Implement rate limiting
- Add CSRF protection
- Secure database connections

## Roadmap

### Phase 1 (Current)
- ✅ Basic meeting scheduling
- ✅ FAM program integration
- ✅ Availability management

### Phase 2 (Planned)
- [ ] Real-time notifications
- [ ] Email reminders
- [ ] Video conferencing integration
- [ ] Mobile app (React Native)

### Phase 3 (Future)
- [ ] AI-powered scheduling suggestions
- [ ] Calendar sync (Google, Outlook)
- [ ] Analytics dashboard
- [ ] Group meeting support

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Use meaningful variable names
- Comment complex logic
- Follow existing code structure
- Test before committing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- **Dhriti Harish Jamadagni**  - [YourGitHub](https://github.com/dhritij27)

## Acknowledgments

- Lucide Icons for beautiful icons
- Inspiration from university scheduling systems
- Community feedback and contributions


## Project Status

**Current Version**: 1.0.0  
**Status**: Active Development  
**Last Updated**: November 2025

---

### Quick Start Commands

```bash
# Setup
git clone <repo-url>
cd academic-meeting-scheduler
mysql -u root -p < database/schema.sql

# Development
python -m http.server 8000

# Access
open http://localhost:8000/src/index.html
```

### Environment Variables

Create a `.env` file:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=meeting_scheduler
PORT=8000
```

---

**Made with ❤️ for better academic collaboration**
