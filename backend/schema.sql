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
    UNIQUE KEY unique_room_slot (room_id, slot_id, meeting_date),
    CONSTRAINT chk_meeting_date CHECK (meeting_date >= CURDATE())
);

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
