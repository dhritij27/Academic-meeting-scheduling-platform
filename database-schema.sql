-- Academic Meeting Scheduler Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'professor', 'fam')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    srn VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Professors table
CREATE TABLE IF NOT EXISTS professors (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    staff_id VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    courses TEXT[],
    office_location VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- FAMs (First-year Academic Mentors) table
CREATE TABLE IF NOT EXISTS fams (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    srn VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL,
    specialization TEXT,
    bio TEXT,
    rating DECIMAL(3,2) DEFAULT 0.00,
    mentees INTEGER DEFAULT 0,
    max_mentees INTEGER DEFAULT 10,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- FAM Mentees relationship table
CREATE TABLE IF NOT EXISTS fam_mentees (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    fam_id UUID REFERENCES fams(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(fam_id, student_id)
);

-- Meetings table
CREATE TABLE IF NOT EXISTS meetings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    category VARCHAR(50) NOT NULL CHECK (category IN ('Student-Professor', 'Student-FAM', 'Peer-to-Peer')),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    professor_id UUID REFERENCES professors(id) ON DELETE SET NULL,
    fam_id UUID REFERENCES fams(id) ON DELETE SET NULL,
    peer_student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    meeting_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('Online', 'Offline')),
    purpose TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Completed', 'Cancelled')),
    location VARCHAR(255),
    meeting_link TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Availability table
CREATE TABLE IF NOT EXISTS availability (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    day_of_week VARCHAR(20) NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_recurring BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(meeting_date);
CREATE INDEX IF NOT EXISTS idx_meetings_student ON meetings(student_id);
CREATE INDEX IF NOT EXISTS idx_meetings_professor ON meetings(professor_id);
CREATE INDEX IF NOT EXISTS idx_meetings_fam ON meetings(fam_id);
CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status);
CREATE INDEX IF NOT EXISTS idx_availability_user ON availability(user_id);
CREATE INDEX IF NOT EXISTS idx_availability_day ON availability(day_of_week);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE professors ENABLE ROW LEVEL SECURITY;
ALTER TABLE fams ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE availability ENABLE ROW LEVEL SECURITY;
ALTER TABLE fam_mentees ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Policies for students table
CREATE POLICY "Students can view their own data" ON students
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Students can update their own data" ON students
    FOR UPDATE USING (user_id = auth.uid());

-- Policies for professors table
CREATE POLICY "Professors can view their own data" ON professors
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Professors can update their own data" ON professors
    FOR UPDATE USING (user_id = auth.uid());

-- Policies for FAMs table
CREATE POLICY "FAMs can view their own data" ON fams
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "FAMs can update their own data" ON fams
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Anyone can view available FAMs" ON fams
    FOR SELECT USING (is_available = true);

-- Policies for meetings table
CREATE POLICY "Users can view their own meetings" ON meetings
    FOR SELECT USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid()) OR
        professor_id IN (SELECT id FROM professors WHERE user_id = auth.uid()) OR
        fam_id IN (SELECT id FROM fams WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can create meetings" ON meetings
    FOR INSERT WITH CHECK (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can update their own meetings" ON meetings
    FOR UPDATE USING (
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid()) OR
        professor_id IN (SELECT id FROM professors WHERE user_id = auth.uid()) OR
        fam_id IN (SELECT id FROM fams WHERE user_id = auth.uid())
    );

-- Policies for availability table
CREATE POLICY "Users can view their own availability" ON availability
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can manage their own availability" ON availability
    FOR ALL USING (user_id = auth.uid());

-- Insert sample data
INSERT INTO users (email, password_hash, role) VALUES
    ('student1@university.edu', '$2a$10$dummy_hash', 'student'),
    ('student2@university.edu', '$2a$10$dummy_hash', 'student'),
    ('student3@university.edu', '$2a$10$dummy_hash', 'student'),
    ('prof1@university.edu', '$2a$10$dummy_hash', 'professor'),
    ('prof2@university.edu', '$2a$10$dummy_hash', 'professor'),
    ('prof3@university.edu', '$2a$10$dummy_hash', 'professor'),
    ('fam1@university.edu', '$2a$10$dummy_hash', 'fam'),
    ('fam2@university.edu', '$2a$10$dummy_hash', 'fam'),
    ('fam3@university.edu', '$2a$10$dummy_hash', 'fam')
ON CONFLICT (email) DO NOTHING;

-- Insert sample students
INSERT INTO students (user_id, name, srn, department, year) VALUES
    ((SELECT id FROM users WHERE email = 'student1@university.edu'), 'Meera Iyer', 'SRN2024001', 'Computer Science', 1),
    ((SELECT id FROM users WHERE email = 'student2@university.edu'), 'Aisha Patel', 'SRN2024005', 'Computer Science', 1),
    ((SELECT id FROM users WHERE email = 'student3@university.edu'), 'Dev Sharma', 'SRN2024006', 'Computer Science', 1)
ON CONFLICT (srn) DO NOTHING;

-- Insert sample professors
INSERT INTO professors (user_id, name, staff_id, department, courses, office_location, email, phone) VALUES
    ((SELECT id FROM users WHERE email = 'prof1@university.edu'), 'Dr. Rajesh Kumar', 'PROF001', 'Computer Science', ARRAY['Data Structures and Algorithms'], 'Block A, Room 301', 'rajesh.kumar@university.edu', '+91-9876543210'),
    ((SELECT id FROM users WHERE email = 'prof2@university.edu'), 'Dr. Priya Sharma', 'PROF002', 'Computer Science', ARRAY['Database Management Systems'], 'Block A, Room 305', 'priya.sharma@university.edu', '+91-9876543211'),
    ((SELECT id FROM users WHERE email = 'prof3@university.edu'), 'Dr. Suresh Patel', 'PROF005', 'Computer Science', ARRAY['Machine Learning'], 'Block A, Room 310', 'suresh.patel@university.edu', '+91-9876543214')
ON CONFLICT (staff_id) DO NOTHING;

-- Insert sample FAMs
INSERT INTO fams (user_id, name, srn, department, year, specialization, bio, rating, mentees, max_mentees, is_available) VALUES
    ((SELECT id FROM users WHERE email = 'fam1@university.edu'), 'Ishaan Gupta', 'SRN2022001', 'Computer Science', 3, 'Data Structures, Web Development', 'Hi! I am a third-year CS student passionate about algorithms and web dev. Happy to help with course selection and coding doubts!', 4.75, 3, 8, true),
    ((SELECT id FROM users WHERE email = 'fam2@university.edu'), 'Tanvi Das', 'SRN2022004', 'Computer Science', 3, 'Machine Learning, Python', 'CS senior specializing in ML. Can help with Python programming, data science, and project ideas. Always happy to chat!', 4.90, 2, 10, true),
    ((SELECT id FROM users WHERE email = 'fam3@university.edu'), 'Rohan Mehta', 'SRN2023008', 'Computer Science', 2, 'Competitive Programming, DSA', 'Competitive programmer with experience in coding contests. Can help you prepare for placements and improve problem-solving skills!', 4.70, 1, 7, true)
ON CONFLICT (srn) DO NOTHING;

-- Insert sample availability
INSERT INTO availability (user_id, day_of_week, start_time, end_time) VALUES
    ((SELECT id FROM users WHERE email = 'student1@university.edu'), 'Monday', '13:00', '15:00'),
    ((SELECT id FROM users WHERE email = 'student1@university.edu'), 'Tuesday', '10:00', '12:00'),
    ((SELECT id FROM users WHERE email = 'student1@university.edu'), 'Wednesday', '15:00', '17:00'),
    ((SELECT id FROM users WHERE email = 'student1@university.edu'), 'Thursday', '10:00', '12:00'),
    ((SELECT id FROM users WHERE email = 'student1@university.edu'), 'Friday', '11:00', '13:00');

-- Insert sample meetings
INSERT INTO meetings (category, student_id, professor_id, meeting_date, start_time, end_time, type, purpose, status, location, meeting_link) VALUES
    ('Student-Professor', (SELECT id FROM students WHERE srn = 'SRN2024001'), (SELECT id FROM professors WHERE staff_id = 'PROF001'), '2025-10-18', '14:00', '14:30', 'Offline', 'Course selection advice', 'Scheduled', 'Block A, Room 301', NULL),
    ('Student-Professor', (SELECT id FROM students WHERE srn = 'SRN2024001'), (SELECT id FROM professors WHERE staff_id = 'PROF002'), '2025-10-08', '14:00', '14:30', 'Offline', 'Database project discussion', 'Completed', 'Block A, Room 305', NULL),
    ('Student-FAM', (SELECT id FROM students WHERE srn = 'SRN2024001'), NULL, (SELECT id FROM fams WHERE srn = 'SRN2022001'), '2025-10-17', '11:30', '12:00', 'Online', 'Help with Data Structures assignment', 'Scheduled', NULL, 'https://meet.google.com/fam-meet-001'),
    ('Student-FAM', (SELECT id FROM students WHERE srn = 'SRN2024001'), NULL, (SELECT id FROM fams WHERE srn = 'SRN2022004'), '2025-10-10', '15:00', '15:30', 'Online', 'Machine Learning concepts introduction', 'Completed', NULL, 'https://meet.google.com/fam-meet-002'),
    ('Peer-to-Peer', (SELECT id FROM students WHERE srn = 'SRN2024001'), NULL, NULL, (SELECT id FROM students WHERE srn = 'SRN2024006'), '2025-10-19', '11:00', '12:00', 'Offline', 'Python programming practice', 'Scheduled', 'Library, Study Room 5', NULL);
