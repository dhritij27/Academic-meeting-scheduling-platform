-- Enable strict SQL mode
SET SQL_MODE = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION';

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS academic_meetings;
USE academic_meetings;

-- Users table (faculty, staff, etc.)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('professor', 'student', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Meeting rooms table
CREATE TABLE IF NOT EXISTS meeting_rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time slots table
CREATE TABLE IF NOT EXISTS time_slots (
    slot_id INT AUTO_INCREMENT PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    day_of_week ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday') NOT NULL,
    is_recurring BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_slot (start_time, end_time, day_of_week)
);

-- User availability (when users are free)
CREATE TABLE IF NOT EXISTS user_availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    slot_id INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES time_slots(slot_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_slot (user_id, slot_id)
);

-- Scheduled meetings
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    room_id INT,
    slot_id INT NOT NULL,
    meeting_date DATE NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    FOREIGN KEY (room_id) REFERENCES meeting_rooms(room_id) ON DELETE SET NULL,
    FOREIGN KEY (slot_id) REFERENCES time_slots(slot_id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_room_slot (room_id, slot_id, meeting_date)
);

-- Trigger to validate meeting date
DELIMITER //
CREATE TRIGGER before_meeting_insert_update
BEFORE INSERT ON meetings
FOR EACH ROW
BEGIN
    IF NEW.meeting_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Meeting date cannot be in the past';
    END IF;
END//

CREATE TRIGGER before_meeting_update
BEFORE UPDATE ON meetings
FOR EACH ROW
BEGIN
    IF NEW.meeting_date < CURDATE() THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Meeting date cannot be in the past';
    END IF;
END//

DELIMITER ;

-- Meeting participants
CREATE TABLE IF NOT EXISTS meeting_participants (
    meeting_id INT,
    user_id INT,
    response ENUM('accepted', 'declined', 'pending') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (meeting_id, user_id),
    FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Trigger to prevent double-booking of users
DELIMITER //
CREATE TRIGGER before_meeting_participant_insert
BEFORE INSERT ON meeting_participants
FOR EACH ROW
BEGIN
    DECLARE participant_count INT;
    
    -- Check if user is already in another meeting at the same time
    SELECT COUNT(*) INTO participant_count
    FROM meeting_participants mp
    JOIN meetings m ON mp.meeting_id = m.meeting_id
    JOIN meetings new_meeting ON m.slot_id = new_meeting.slot_id 
        AND m.meeting_date = new_meeting.meeting_date
    WHERE mp.user_id = NEW.user_id 
        AND m.status = 'scheduled'
        AND new_meeting.meeting_id = NEW.meeting_id
        AND mp.response != 'declined';
    
    IF participant_count > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'User is already in another meeting at this time';
    END IF;
END //

-- Trigger to update user availability when they schedule a meeting
CREATE TRIGGER after_meeting_schedule
AFTER INSERT ON meeting_participants
FOR EACH ROW
BEGIN
    -- Mark user as unavailable for this time slot
    INSERT INTO user_availability (user_id, slot_id, is_available, created_at)
    SELECT NEW.user_id, m.slot_id, FALSE, NOW()
    FROM meetings m
    WHERE m.meeting_id = NEW.meeting_id
    ON DUPLICATE KEY UPDATE is_available = FALSE, created_at = NOW();
END //

-- Trigger to update user availability when a meeting is cancelled
CREATE TRIGGER after_meeting_cancelled
AFTER UPDATE ON meetings
FOR EACH ROW
BEGIN
    IF OLD.status != 'cancelled' AND NEW.status = 'cancelled' THEN
        -- Mark all participants as available for this time slot
        UPDATE user_availability ua
        JOIN meeting_participants mp ON ua.user_id = mp.user_id
        SET ua.is_available = TRUE
        WHERE mp.meeting_id = NEW.meeting_id
        AND ua.slot_id = NEW.slot_id;
    END IF;
END //

-- Procedure to get user's free slots
CREATE PROCEDURE get_user_free_slots(IN p_user_id INT, IN p_date DATE)
BEGIN
    -- Get day of week (1=Sunday, 2=Monday, ..., 7=Saturday)
    DECLARE day_name VARCHAR(10);
    SET day_name = DAYNAME(p_date);
    
    -- Get all time slots for the day of week
    SELECT 
        ts.slot_id,
        ts.start_time,
        ts.end_time,
        p_date AS date,
        CASE 
            WHEN m.meeting_id IS NOT NULL THEN 'booked'
            WHEN ua.is_available = FALSE THEN 'unavailable'
            ELSE 'available'
        END AS status
    FROM time_slots ts
    LEFT JOIN user_availability ua ON ts.slot_id = ua.slot_id 
        AND ua.user_id = p_user_id 
        AND ua.is_available = FALSE
    LEFT JOIN meetings m ON ts.slot_id = m.slot_id 
        AND m.meeting_date = p_date 
        AND m.status = 'scheduled'
        AND m.meeting_id IN (
            SELECT meeting_id 
            FROM meeting_participants 
            WHERE user_id = p_user_id 
            AND response != 'declined'
        )
    WHERE LOWER(ts.day_of_week) = LOWER(day_name)
    ORDER BY ts.start_time;
END //

-- Procedure to get available rooms for a time slot
CREATE PROCEDURE get_available_rooms(IN p_slot_id INT, IN p_date DATE)
BEGIN
    SELECT r.*
    FROM meeting_rooms r
    WHERE r.is_active = TRUE
    AND r.room_id NOT IN (
        SELECT m.room_id
        FROM meetings m
        WHERE m.slot_id = p_slot_id
        AND m.meeting_date = p_date
        AND m.status = 'scheduled'
        AND m.room_id IS NOT NULL
    )
    ORDER BY r.capacity;
END //

DELIMITER ;

-- Insert some sample data
INSERT IGNORE INTO time_slots (start_time, end_time, day_of_week, is_recurring) VALUES
('09:00:00', '10:00:00', 'monday', TRUE),
('10:00:00', '11:00:00', 'monday', TRUE),
('11:00:00', '12:00:00', 'monday', TRUE),
('14:00:00', '15:00:00', 'monday', TRUE),
('15:00:00', '16:00:00', 'monday', TRUE),
('16:00:00', '17:00:00', 'monday', TRUE),
('09:00:00', '10:00:00', 'tuesday', TRUE),
('10:00:00', '11:00:00', 'tuesday', TRUE),
('11:00:00', '12:00:00', 'tuesday', TRUE),
('14:00:00', '15:00:00', 'tuesday', TRUE),
('15:00:00', '16:00:00', 'tuesday', TRUE),
('16:00:00', '17:00:00', 'tuesday', TRUE);

-- Insert some sample rooms
INSERT IGNORE INTO meeting_rooms (name, capacity) VALUES
('Conference Room A', 10),
('Conference Room B', 8),
('Seminar Hall', 50),
('Faculty Lounge', 15);

-- Create a function to check room availability
DELIMITER //
CREATE FUNCTION is_room_available(p_room_id INT, p_slot_id INT, p_date DATE) 
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE is_booked INT;
    
    SELECT COUNT(*) INTO is_booked
    FROM meetings
    WHERE room_id = p_room_id
    AND slot_id = p_slot_id
    AND meeting_date = p_date
    AND status = 'scheduled';
    
    RETURN is_booked = 0;
END //

-- Create FAMs table
CREATE TABLE IF NOT EXISTS fams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(255) NOT NULL,
    srn VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    specialization TEXT,
    bio TEXT,
    rating DECIMAL(3,2) DEFAULT 0.00,
    mentees INT DEFAULT 0,
    max_mentees INT DEFAULT 10,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create students table if it doesn't exist
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(255) NOT NULL,
    srn VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create fam_mentees relationship table
CREATE TABLE IF NOT EXISTS fam_mentees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fam_id INT NOT NULL,
    student_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fam_id, student_id),
    FOREIGN KEY (fam_id) REFERENCES fams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Create subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_code VARCHAR(20) UNIQUE NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert sample subjects
INSERT INTO subjects (subject_code, subject_name, department, credits) VALUES
    ('CS101', 'Introduction to Programming', 'Computer Science', 4),
    ('CS201', 'Data Structures', 'Computer Science', 4),
    ('CS301', 'Algorithms', 'Computer Science', 4),
    ('CS401', 'Database Systems', 'Computer Science', 3),
    ('CS501', 'Machine Learning', 'Computer Science', 4),
    ('IT101', 'Introduction to IT', 'Information Technology', 3),
    ('IT201', 'Networking Fundamentals', 'Information Technology', 4),
    ('IT301', 'Cybersecurity Basics', 'Information Technology', 4),
    ('MATH101', 'Calculus I', 'Mathematics', 4),
    ('MATH201', 'Linear Algebra', 'Mathematics', 3)
ON DUPLICATE KEY UPDATE
    subject_name = VALUES(subject_name),
    department = VALUES(department),
    credits = VALUES(credits),
    updated_at = CURRENT_TIMESTAMP;

-- Create student_grades table
CREATE TABLE IF NOT EXISTS student_grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT,
    fam_id INT NOT NULL,
    grade VARCHAR(2) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    academic_year VARCHAR(10) NOT NULL,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    FOREIGN KEY (fam_id) REFERENCES fams(id) ON DELETE CASCADE,
    UNIQUE KEY unique_grade_entry (student_id, subject_id, semester, academic_year)
);

-- Insert sample FAMs
INSERT INTO fams (user_id, name, srn, department, year, specialization, bio, rating, max_mentees) VALUES
    (NULL, 'John Doe', 'FAM001', 'Computer Science', 3, 'Algorithms, Web Development', 'Senior CS student with experience in competitive programming', 4.8, 8),
    (NULL, 'Jane Smith', 'FAM002', 'Computer Science', 4, 'Machine Learning, Python', 'ML enthusiast with internship experience at top tech companies', 4.9, 10),
    (NULL, 'Alex Johnson', 'FAM003', 'Information Technology', 3, 'Cybersecurity, Networking', 'Cyber security researcher and CTF player', 4.7, 6)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    department = VALUES(department),
    year = VALUES(year),
    specialization = VALUES(specialization),
    bio = VALUES(bio),
    rating = VALUES(rating),
    max_mentees = VALUES(max_mentees),
    updated_at = CURRENT_TIMESTAMP;

-- Insert sample students
INSERT INTO students (user_id, name, srn, department, year) VALUES
    (NULL, 'Michael Brown', 'SRN2023001', 'Computer Science', 1),
    (NULL, 'Sarah Wilson', 'SRN2023002', 'Computer Science', 1),
    (NULL, 'David Lee', 'SRN2023003', 'Information Technology', 1),
    (NULL, 'Emma Garcia', 'SRN2023004', 'Computer Science', 1),
    (NULL, 'James Miller', 'SRN2023005', 'Information Technology', 1)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    department = VALUES(department),
    year = VALUES(year),
    updated_at = CURRENT_TIMESTAMP;

-- Assign students to FAMs
INSERT INTO fam_mentees (fam_id, student_id) VALUES
    ((SELECT id FROM fams WHERE srn = 'FAM001' LIMIT 1), (SELECT id FROM students WHERE srn = 'SRN2023001' LIMIT 1)),
    ((SELECT id FROM fams WHERE srn = 'FAM001' LIMIT 1), (SELECT id FROM students WHERE srn = 'SRN2023002' LIMIT 1)),
    ((SELECT id FROM fams WHERE srn = 'FAM002' LIMIT 1), (SELECT id FROM students WHERE srn = 'SRN2023003' LIMIT 1)),
    ((SELECT id FROM fams WHERE srn = 'FAM002' LIMIT 1), (SELECT id FROM students WHERE srn = 'SRN2023004' LIMIT 1)),
    ((SELECT id FROM fams WHERE srn = 'FAM003' LIMIT 1), (SELECT id FROM students WHERE srn = 'SRN2023005' LIMIT 1))
ON DUPLICATE KEY UPDATE
    assigned_at = CURRENT_TIMESTAMP;

-- Update mentee counts
UPDATE fams f
SET mentees = (
    SELECT COUNT(*) 
    FROM fam_mentees fm 
    WHERE fm.fam_id = f.id
);

-- Insert sample grades
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
    updated_at = CURRENT_TIMESTAMP;

DELIMITER ;

-- Create a view for daily schedules
CREATE VIEW daily_schedule AS
SELECT 
    m.meeting_id,
    m.title,
    m.meeting_date,
    ts.start_time,
    ts.end_time,
    mr.name AS room_name,
    u.name AS organizer,
    m.status
FROM meetings m
JOIN time_slots ts ON m.slot_id = ts.slot_id
LEFT JOIN meeting_rooms mr ON m.room_id = mr.room_id
JOIN users u ON m.created_by = u.user_id
WHERE m.status = 'scheduled'
ORDER BY m.meeting_date, ts.start_time;
