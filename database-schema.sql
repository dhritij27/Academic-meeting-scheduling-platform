-- Academic Meeting Scheduler Database Schema
-- Run this SQL in your MySQL Editor

-- MySQL schema for Academic Meeting Scheduling Platform
-- Drop existing tables if they exist (be careful with this in production)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS availability;
DROP TABLE IF EXISTS meetings;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS fams;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- Create users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'professor', 'fam', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create students table
CREATE TABLE students (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    srn VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100),
    year_of_study INT,
    gpa DECIMAL(3,2),
    cgpa DECIMAL(3,2),
    fam_id VARCHAR(36),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create professors table
CREATE TABLE professors (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    staff_id VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100),
    designation VARCHAR(100),
    office_location VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create fams table
CREATE TABLE fams (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    srn VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(100),
    year INT,
    specialization TEXT,
    bio TEXT,
    rating DECIMAL(3,2),
    mentees INT DEFAULT 0,
    max_mentees INT DEFAULT 5,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Add foreign key from students to fams
ALTER TABLE students
ADD FOREIGN KEY (fam_id) REFERENCES fams(id) ON DELETE SET NULL;

-- Create meetings table
CREATE TABLE meetings (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    category ENUM('Student-Professor', 'Student-FAM') NOT NULL,
    student_id VARCHAR(36) NOT NULL,
    professor_id VARCHAR(36),
    fam_id VARCHAR(36),
    meeting_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    type ENUM('Online', 'Offline') NOT NULL,
    purpose TEXT,
    status ENUM('Scheduled', 'Completed', 'Cancelled', 'No-show') DEFAULT 'Scheduled',
    location VARCHAR(255),
    meeting_link VARCHAR(512),
    grade VARCHAR(2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (professor_id) REFERENCES professors(id) ON DELETE SET NULL,
    FOREIGN KEY (fam_id) REFERENCES fams(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Create availability table
CREATE TABLE availability (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create indexes for better performance
CREATE INDEX idx_meetings_date ON meetings(meeting_date);
CREATE INDEX idx_meetings_student ON meetings(student_id);
CREATE INDEX idx_meetings_professor ON meetings(professor_id);
CREATE INDEX idx_meetings_fam ON meetings(fam_id);
CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_availability_user ON availability(user_id);
CREATE INDEX idx_availability_day ON availability(day_of_week);

-- Insert sample data
-- Insert sample users (20 users total)
INSERT INTO users (id, email, password_hash, role) VALUES
    -- Students (10)
    (UUID(), 'student1@university.edu', '$2a$10$xJwL5J8b6o1U7wV8QeZ9peYV1XHvU8Jk1YbXKQmWnZp9G2hLmNoPq', 'student'),
    (UUID(), 'student2@university.edu', '$2a$10$yH9pV8sL6fRtNkQwXv5y0eJp1LmNoPqRsTuVwXyZz3A2B4C5D6E7F', 'student'),
    (UUID(), 'student3@university.edu', '$2a$10$zI9qR7tYu2w3v4x5z6B7V8cX9Z0aB1C2D3E4F5G6H7I8J9K0L1M2', 'student'),
    (UUID(), 'student4@university.edu', '$2a$10$aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0uV1wX2yZ3A4B5C6D7E8F9G', 'student'),
    (UUID(), 'student5@university.edu', '$2a$10$hI9J8k7L6m5N4b3V2c1X0z9A8S7D6F5G4H3J2K1L0M9N8B7V6C5X', 'student'),
    (UUID(), 'student6@university.edu', '$2a$10$qWeRtYuIoPaSdFgHjKlZiOxCvBnMlKjIhUyGtFrDeRtYzXcVbNmKj', 'student'),
    (UUID(), 'student7@university.edu', '$2a$10$mKjNhgFdSqWeRtYuIoPaSdFgHjKlZiOxCvBnMlKjIhUyGtFrDeRtYz', 'student'),
    (UUID(), 'student8@university.edu', '$2a$10$sXcVbNmKlOpLkJhUvGtFrDeRtYzXcVbNmKlOpLkJhUvGtFrDeRtYz', 'student'),
    (UUID(), 'student9@university.edu', '$2a$10$dFgHjKlZiOxCvBnMlKjIhUyGtFrDeRtYzXcVbNmKlOpLkJhUvGtFrD', 'student'),
    (UUID(), 'student10@university.edu', '$2a$10$kLmNoPqRsTuVwXyZz3A2B4C5D6E7F8G9H0I1J2K3L4M5N6O7P8Q9R', 'student'),
    
    -- Professors (5)
    (UUID(), 'prof1@university.edu', '$2a$10$pOlkIjUhYgTrDeSwAqWeRtYuIoPaSdFgHjKlZiOxCvBnMlKjIhUyG', 'professor'),
    (UUID(), 'prof2@university.edu', '$2a$10$qWeRtYuIoPaSdFgHjKlZiOxCvBnMlKjIhUyGtFrDeRtYzXcVbNmKl', 'professor'),
    (UUID(), 'prof3@university.edu', '$2a$10$mKjNhgFdSqWeRtYuIoPaSdFgHjKlZiOxCvBnMlKjIhUyGtFrDeRtYz', 'professor'),
    (UUID(), 'prof4@university.edu', '$2a$10$sXcVbNmKlOpLkJhUvGtFrDeRtYzXcVbNmKlOpLkJhUvGtFrDeRtYz', 'professor'),
    (UUID(), 'prof5@university.edu', '$2a$10$dFgHjKlZiOxCvBnMlKjIhUyGtFrDeRtYzXcVbNmKlOpLkJhUvGtFrD', 'professor'),
    
    -- FAMs (3)
    (UUID(), 'fam1@university.edu', '$2a$10$kLmNoPqRsTuVwXyZz3A2B4C5D6E7F8G9H0I1J2K3L4M5N6O7P8Q9R', 'fam'),
    (UUID(), 'fam2@university.edu', '$2a$10$pOlkIjUhYgTrDeSwAqWeRtYuIoPaSdFgHjKlZiOxCvBnMlKjIhUyG', 'fam'),
    (UUID(), 'fam3@university.edu', '$2a$10$qWeRtYuIoPaSdFgHjKlZiOxCvBnMlKjIhUyGtFrDeRtYzXcVbNmKl', 'fam'),
    
    -- Admin
    (UUID(), 'admin@university.edu', '$2a$10$adminpass1234567890123456789012345678901234567890123456789012', 'admin');

-- Insert sample students (10 students)
SET @student1_id = (SELECT id FROM users WHERE email = 'student1@university.edu');
SET @student2_id = (SELECT id FROM users WHERE email = 'student2@university.edu');
SET @student3_id = (SELECT id FROM users WHERE email = 'student3@university.edu');
SET @student4_id = (SELECT id FROM users WHERE email = 'student4@university.edu');
SET @student5_id = (SELECT id FROM users WHERE email = 'student5@university.edu');
SET @student6_id = (SELECT id FROM users WHERE email = 'student6@university.edu');
SET @student7_id = (SELECT id FROM users WHERE email = 'student7@university.edu');
SET @student8_id = (SELECT id FROM users WHERE email = 'student8@university.edu');
SET @student9_id = (SELECT id FROM users WHERE email = 'student9@university.edu');
SET @student10_id = (SELECT id FROM users WHERE email = 'student10@university.edu');

INSERT INTO students (id, user_id, name, srn, department, year_of_study, gpa, cgpa) VALUES
    (UUID(), @student1_id, 'Rahul Sharma', 'SRN2024001', 'Computer Science', 2, 3.5, 3.6),
    (UUID(), @student2_id, 'Priya Patel', 'SRN2024002', 'Electronics', 1, 3.2, 3.3),
    (UUID(), @student3_id, 'Amit Kumar', 'SRN2024003', 'Mechanical', 3, 3.8, 3.7),
    (UUID(), @student4_id, 'Sneha Reddy', 'SRN2024004', 'Computer Science', 2, 3.9, 3.8),
    (UUID(), @student5_id, 'Vikram Singh', 'SRN2024005', 'Electrical', 4, 3.4, 3.5),
    (UUID(), @student6_id, 'Ananya Gupta', 'SRN2024006', 'Biotechnology', 1, 3.7, 3.7),
    (UUID(), @student7_id, 'Rohan Mehta', 'SRN2024007', 'Computer Science', 3, 3.6, 3.5),
    (UUID(), @student8_id, 'Neha Joshi', 'SRN2024008', 'Electronics', 2, 3.9, 3.8),
    (UUID(), @student9_id, 'Arjun Desai', 'SRN2024009', 'Mechanical', 4, 3.3, 3.4),
    (UUID(), @student10_id, 'Meera Nair', 'SRN2024010', 'Computer Science', 1, 3.8, 3.8);

-- Insert sample professors (5 professors)
SET @prof1_id = (SELECT id FROM users WHERE email = 'prof1@university.edu');
SET @prof2_id = (SELECT id FROM users WHERE email = 'prof2@university.edu');
SET @prof3_id = (SELECT id FROM users WHERE email = 'prof3@university.edu');
SET @prof4_id = (SELECT id FROM users WHERE email = 'prof4@university.edu');
SET @prof5_id = (SELECT id FROM users WHERE email = 'prof5@university.edu');

INSERT INTO professors (id, user_id, name, staff_id, department, designation, office_location) VALUES
    (UUID(), @prof1_id, 'Dr. Rajesh Kumar', 'PROF001', 'Computer Science', 'Professor', 'Block A, Room 301'),
    (UUID(), @prof2_id, 'Dr. Sunita Iyer', 'PROF002', 'Electronics', 'Associate Professor', 'Block B, Room 205'),
    (UUID(), @prof3_id, 'Dr. Amit Patel', 'PROF003', 'Mechanical', 'Professor', 'Block C, Room 102'),
    (UUID(), @prof4_id, 'Dr. Priya Sharma', 'PROF004', 'Computer Science', 'Assistant Professor', 'Block A, Room 205'),
    (UUID(), @prof5_id, 'Dr. Ramesh Nair', 'PROF005', 'Electrical', 'Professor', 'Block D, Room 310');

-- Insert sample FAMs (3 FAMs)
SET @fam1_id = (SELECT id FROM users WHERE email = 'fam1@university.edu');
SET @fam2_id = (SELECT id FROM users WHERE email = 'fam2@university.edu');
SET @fam3_id = (SELECT id FROM users WHERE email = 'fam3@university.edu');

INSERT INTO fams (id, user_id, name, srn, department, year, specialization, bio, rating, mentees, max_mentees, is_available) VALUES
    (UUID(), @fam1_id, 'Ishaan Gupta', 'SRN2022001', 'Computer Science', 3, 'Data Structures, Web Development', 'Third-year CS student passionate about algorithms and web dev. Happy to help with course selection and coding doubts!', 4.75, 3, 8, true),
    (UUID(), @fam2_id, 'Tanvi Das', 'SRN2022004', 'Computer Science', 4, 'Machine Learning, Python', 'CS senior specializing in ML. Can help with Python programming, data science, and project ideas.', 4.90, 2, 10, true),
    (UUID(), @fam3_id, 'Rahul Mehta', 'SRN2022007', 'Electronics', 3, 'Embedded Systems, IoT', 'Passionate about electronics and IoT projects. Can help with circuit design and microcontrollers.', 4.80, 1, 6, true);

-- Update students with FAM assignments (assigning students to FAMs)
UPDATE students SET fam_id = (SELECT id FROM fams WHERE srn = 'SRN2022001') WHERE srn IN ('SRN2024001', 'SRN2024003', 'SRN2024007');
UPDATE students SET fam_id = (SELECT id FROM fams WHERE srn = 'SRN2022004') WHERE srn IN ('SRN2024002', 'SRN2024004', 'SRN2024008', 'SRN2024010');
UPDATE students SET fam_id = (SELECT id FROM fams WHERE srn = 'SRN2022007') WHERE srn IN ('SRN2024005', 'SRN2024006', 'SRN2024009');

-- Insert sample availability for students, professors, and FAMs
-- Student 1
INSERT INTO availability (id, user_id, day_of_week, start_time, end_time) VALUES
    (UUID(), @student1_id, 'Monday', '13:00:00', '15:00:00'),
    (UUID(), @student1_id, 'Tuesday', '10:00:00', '12:00:00'),
    (UUID(), @student1_id, 'Wednesday', '15:00:00', '17:00:00'),
    (UUID(), @student1_id, 'Thursday', '10:00:00', '12:00:00'),
    (UUID(), @student1_id, 'Friday', '11:00:00', '13:00:00'),
    
    -- Student 2
    (UUID(), @student2_id, 'Monday', '09:00:00', '11:00:00'),
    (UUID(), @student2_id, 'Wednesday', '14:00:00', '16:00:00'),
    (UUID(), @student2_id, 'Friday', '10:00:00', '12:00:00'),
    
    -- Professor 1
    (UUID(), @prof1_id, 'Monday', '10:00:00', '12:00:00'),
    (UUID(), @prof1_id, 'Tuesday', '14:00:00', '16:00:00'),
    (UUID(), @prof1_id, 'Thursday', '11:00:00', '13:00:00'),
    
    -- Professor 2
    (UUID(), @prof2_id, 'Wednesday', '09:00:00', '11:00:00'),
    (UUID(), @prof2_id, 'Thursday', '14:00:00', '16:00:00'),
    
    -- FAM 1
    (UUID(), @fam1_id, 'Monday', '10:00:00', '12:00:00'),
    (UUID(), @fam1_id, 'Wednesday', '14:00:00', '16:00:00'),
    (UUID(), @fam1_id, 'Friday', '11:00:00', '13:00:00'),
    
    -- FAM 2
    (UUID(), @fam2_id, 'Tuesday', '09:00:00', '11:00:00'),
    (UUID(), @fam2_id, 'Thursday', '13:00:00', '15:00:00');

-- Insert sample meetings (15 meetings)
SET @student1_db_id = (SELECT id FROM students WHERE srn = 'SRN2024001');
SET @student2_db_id = (SELECT id FROM students WHERE srn = 'SRN2024002');
SET @student3_db_id = (SELECT id FROM students WHERE srn = 'SRN2024003');
SET @student4_db_id = (SELECT id FROM students WHERE srn = 'SRN2024004');
SET @student5_db_id = (SELECT id FROM students WHERE srn = 'SRN2024005');
SET @student6_db_id = (SELECT id FROM students WHERE srn = 'SRN2024006');

SET @prof1_db_id = (SELECT id FROM professors WHERE staff_id = 'PROF001');
SET @prof2_db_id = (SELECT id FROM professors WHERE staff_id = 'PROF002');
SET @prof3_db_id = (SELECT id FROM professors WHERE staff_id = 'PROF003');
SET @prof4_db_id = (SELECT id FROM professors WHERE staff_id = 'PROF004');

SET @fam1_db_id = (SELECT id FROM fams WHERE srn = 'SRN2022001');
SET @fam2_db_id = (SELECT id FROM fams WHERE srn = 'SRN2022004');
SET @fam3_db_id = (SELECT id FROM fams WHERE srn = 'SRN2022007');

INSERT INTO meetings (id, category, student_id, professor_id, fam_id, meeting_date, start_time, end_time, type, purpose, status, location, meeting_link, grade, feedback) VALUES
    -- Student-Professor meetings
    (UUID(), 'Student-Professor', @student1_db_id, @prof1_db_id, NULL, '2025-10-18', '14:00:00', '14:30:00', 'Offline', 'Course selection advice', 'Scheduled', 'Block A, Room 301', NULL, NULL, NULL),
    (UUID(), 'Student-Professor', @student1_db_id, @prof2_db_id, NULL, '2025-10-08', '14:00:00', '14:30:00', 'Offline', 'Database project discussion', 'Completed', 'Block A, Room 305', NULL, 'A', 'Excellent understanding of database concepts.'),
    (UUID(), 'Student-Professor', @student2_db_id, @prof3_db_id, NULL, '2025-10-15', '11:00:00', '11:30:00', 'Online', 'Thesis guidance', 'Scheduled', NULL, 'https://meet.google.com/abc-xyz-123', NULL, NULL),
    (UUID(), 'Student-Professor', @student3_db_id, @prof1_db_id, NULL, '2025-10-10', '10:00:00', '10:30:00', 'Offline', 'Research paper discussion', 'Completed', 'Block A, Room 302', NULL, 'B+', 'Good work, needs more references.'),
    (UUID(), 'Student-Professor', @student4_db_id, @prof4_db_id, NULL, '2025-10-17', '15:00:00', '15:45:00', 'Online', 'Project proposal review', 'Scheduled', NULL, 'https://meet.google.com/def-456-789', NULL, NULL),
    
    -- Student-FAM meetings
    (UUID(), 'Student-FAM', @student1_db_id, NULL, @fam1_db_id, '2025-10-17', '11:30:00', '12:00:00', 'Online', 'Help with Data Structures assignment', 'Scheduled', NULL, 'https://meet.google.com/fam-meet-001', NULL, NULL),
    (UUID(), 'Student-FAM', @student2_db_id, NULL, @fam2_db_id, '2025-10-10', '15:00:00', '15:30:00', 'Online', 'Machine Learning concepts introduction', 'Completed', NULL, 'https://meet.google.com/fam-meet-002', 'A', 'Very helpful session!'),
    (UUID(), 'Student-FAM', @student3_db_id, NULL, @fam3_db_id, '2025-10-12', '16:00:00', '16:30:00', 'Online', 'Circuit design help', 'Completed', NULL, 'https://meet.google.com/fam-meet-003', 'A-', 'Clear explanations, very patient.'),
    (UUID(), 'Student-FAM', @student4_db_id, NULL, @fam1_db_id, '2025-10-19', '14:00:00', '14:30:00', 'Online', 'Web development guidance', 'Scheduled', NULL, 'https://meet.google.com/fam-meet-004', NULL, NULL),
    (UUID(), 'Student-FAM', @student5_db_id, NULL, @fam2_db_id, '2025-10-20', '10:30:00', '11:00:00', 'Online', 'Python data analysis help', 'Scheduled', NULL, 'https://meet.google.com/fam-meet-005', NULL, NULL),
    
    -- Group meetings
    (UUID(), 'Student-Professor', @student1_db_id, @prof1_db_id, NULL, '2025-10-22', '13:00:00', '14:00:00', 'Offline', 'Group project discussion', 'Scheduled', 'Block A, Room 201', NULL, NULL, NULL),
    (UUID(), 'Student-Professor', @student2_db_id, @prof1_db_id, NULL, '2025-10-22', '13:00:00', '14:00:00', 'Offline', 'Group project discussion', 'Scheduled', 'Block A, Room 201', NULL, NULL, NULL),
    (UUID(), 'Student-Professor', @student3_db_id, @prof1_db_id, NULL, '2025-10-22', '13:00:00', '14:00:00', 'Offline', 'Group project discussion', 'Scheduled', 'Block A, Room 201', NULL, NULL, NULL),
    
    -- Upcoming meetings
    (UUID(), 'Student-Professor', @student6_db_id, @prof2_db_id, NULL, '2025-11-05', '11:00:00', '11:30:00', 'Online', 'Thesis topic discussion', 'Scheduled', NULL, 'https://meet.google.com/xyz-123-456', NULL, NULL),
    (UUID(), 'Student-FAM', @student6_db_id, NULL, @fam3_db_id, '2025-11-10', '15:00:00', '15:30:00', 'Online', 'Embedded systems guidance', 'Scheduled', NULL, 'https://meet.google.com/fam-meet-006', NULL, NULL);

-- Update FAM mentees count
UPDATE fams 
SET mentees = (SELECT COUNT(*) FROM students WHERE fam_id = id)
WHERE id IN (SELECT id FROM fams);
