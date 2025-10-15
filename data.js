/**
 * data.js - Data Layer
 * Contains all data structures and simulated database operations
 * In production, these would be replaced with API calls
 */

// Current user data
const data = {
    currentUser: {
        role: 'student',
        id: 13,
        name: 'Meera Iyer',
        srn: 'SRN2024001',
        department: 'Computer Science',
        year: 1
    },

    // All meetings data
    meetings: [
        {
            id: 1,
            category: 'Student-FAM',
            with: 'Ishaan Gupta',
            date: '2025-10-17',
            startTime: '11:30',
            endTime: '12:00',
            type: 'Online',
            purpose: 'Help with Data Structures assignment',
            status: 'Scheduled',
            link: 'https://meet.google.com/fam-meet-001'
        },
        {
            id: 2,
            category: 'Student-Professor',
            with: 'Dr. Rajesh Kumar',
            date: '2025-10-18',
            startTime: '14:00',
            endTime: '14:30',
            type: 'Offline',
            purpose: 'Course selection advice',
            status: 'Scheduled',
            location: 'Block A, Room 301'
        },
        {
            id: 3,
            category: 'Peer-to-Peer',
            with: 'Dev Sharma',
            date: '2025-10-19',
            startTime: '11:00',
            endTime: '12:00',
            type: 'Offline',
            purpose: 'Python programming practice',
            status: 'Scheduled',
            location: 'Library, Study Room 5'
        },
        {
            id: 4,
            category: 'Student-FAM',
            with: 'Tanvi Das',
            date: '2025-10-10',
            startTime: '15:00',
            endTime: '15:30',
            type: 'Online',
            purpose: 'Machine Learning concepts introduction',
            status: 'Completed',
            rating: 5,
            feedback: 'Excellent session!'
        },
        {
            id: 5,
            category: 'Student-Professor',
            with: 'Dr. Priya Sharma',
            date: '2025-10-08',
            startTime: '14:00',
            endTime: '14:30',
            type: 'Offline',
            purpose: 'Database project discussion',
            status: 'Completed',
            location: 'Block A, Room 305'
        }
    ],

    // User availability slots
    availability: [
        { day: 'Monday', start: '13:00', end: '15:00' },
        { day: 'Tuesday', start: '10:00', end: '12:00' },
        { day: 'Wednesday', start: '15:00', end: '17:00' },
        { day: 'Thursday', start: '10:00', end: '12:00' },
        { day: 'Friday', start: '11:00', end: '13:00' }
    ],

    // FAM (First-year Academic Mentors) data
    fams: [
        {
            id: 1,
            name: 'Ishaan Gupta',
            srn: 'SRN2022001',
            department: 'Computer Science',
            year: 3,
            specialization: 'Data Structures, Web Development',
            bio: 'Hi! I am a third-year CS student passionate about algorithms and web dev. Happy to help with course selection and coding doubts!',
            rating: 4.75,
            mentees: 3,
            maxMentees: 8,
            isAvailable: true
        },
        {
            id: 4,
            name: 'Tanvi Das',
            srn: 'SRN2022004',
            department: 'Computer Science',
            year: 3,
            specialization: 'Machine Learning, Python',
            bio: 'CS senior specializing in ML. Can help with Python programming, data science, and project ideas. Always happy to chat!',
            rating: 4.90,
            mentees: 2,
            maxMentees: 10,
            isAvailable: true
        },
        {
            id: 5,
            name: 'Rohan Mehta',
            srn: 'SRN2023008',
            department: 'Computer Science',
            year: 2,
            specialization: 'Competitive Programming, DSA',
            bio: 'Competitive programmer with experience in coding contests. Can help you prepare for placements and improve problem-solving skills!',
            rating: 4.70,
            mentees: 1,
            maxMentees: 7,
            isAvailable: true
        },
        {
            id: 2,
            name: 'Kavya Menon',
            srn: 'SRN2022002',
            department: 'Electronics',
            year: 3,
            specialization: 'Circuit Design, Embedded Systems',
            bio: 'Third-year Electronics student. I can help with circuit analysis and microcontroller projects. Also happy to share internship tips!',
            rating: 4.60,
            mentees: 2,
            maxMentees: 8,
            isAvailable: true
        },
        {
            id: 3,
            name: 'Krishna Kumar',
            srn: 'SRN2022003',
            department: 'Mathematics',
            year: 3,
            specialization: 'Calculus, Linear Algebra',
            bio: 'Math enthusiast here! I love helping students understand complex mathematical concepts. Let us make math fun together!',
            rating: 4.85,
            mentees: 6,
            maxMentees: 6,
            isAvailable: false
        }
    ],

    // Professors data
    professors: [
        {
            id: 1,
            name: 'Dr. Rajesh Kumar',
            staffId: 'PROF001',
            department: 'Computer Science',
            courses: ['Data Structures and Algorithms'],
            officeLocation: 'Block A, Room 301',
            email: 'rajesh.kumar@university.edu',
            phone: '+91-9876543210'
        },
        {
            id: 2,
            name: 'Dr. Priya Sharma',
            staffId: 'PROF002',
            department: 'Computer Science',
            courses: ['Database Management Systems'],
            officeLocation: 'Block A, Room 305',
            email: 'priya.sharma@university.edu',
            phone: '+91-9876543211'
        },
        {
            id: 5,
            name: 'Dr. Suresh Patel',
            staffId: 'PROF005',
            department: 'Computer Science',
            courses: ['Machine Learning'],
            officeLocation: 'Block A, Room 310',
            email: 'suresh.patel@university.edu',
            phone: '+91-9876543214'
        },
        {
            id: 3,
            name: 'Dr. Anand Menon',
            staffId: 'PROF003',
            department: 'Electronics',
            courses: ['Digital Electronics'],
            officeLocation: 'Block B, Room 201',
            email: 'anand.menon@university.edu',
            phone: '+91-9876543212'
        },
        {
            id: 4,
            name: 'Dr. Kavita Reddy',
            staffId: 'PROF004',
            department: 'Mathematics',
            courses: ['Linear Algebra'],
            officeLocation: 'Block C, Room 102',
            email: 'kavita.reddy@university.edu',
            phone: '+91-9876543213'
        }
    ],

    // Students data (for peer-to-peer meetings)
    students: [
        {
            id: 17,
            name: 'Aisha Patel',
            srn: 'SRN2024005',
            department: 'Computer Science',
            year: 1
        },
        {
            id: 18,
            name: 'Dev Sharma',
            srn: 'SRN2024006',
            department: 'Computer Science',
            year: 1
        },
        {
            id: 7,
            name: 'Ananya Krishnan',
            srn: 'SRN2023002',
            department: 'Computer Science',
            year: 2
        },
        {
            id: 6,
            name: 'Aarav Patel',
            srn: 'SRN2023001',
            department: 'Computer Science',
            year: 2
        }
    ]
};

/**
 * API Simulation Functions
 * These would be replaced with actual API calls in production
 */

// Get all meetings for current user
function getMeetings(status = 'all') {
    if (status === 'all') return data.meetings;
    return data.meetings.filter(m => m.status === status);
}

// Get upcoming meetings
function getUpcomingMeetings() {
    return data.meetings.filter(m => m.status === 'Scheduled');
}

// Get completed meetings
function getCompletedMeetings() {
    return data.meetings.filter(m => m.status === 'Completed');
}

// Get meeting by ID
function getMeetingById(id) {
    return data.meetings.find(m => m.id === id);
}

// Add new meeting
function addMeeting(meetingData) {
    const newMeeting = {
        id: data.meetings.length + 1,
        ...meetingData,
        status: 'Scheduled'
    };
    data.meetings.push(newMeeting);
    return newMeeting;
}

// Cancel meeting
function cancelMeeting(id) {
    const meeting = data.meetings.find(m => m.id === id);
    if (meeting) {
        meeting.status = 'Cancelled';
        return true;
    }
    return false;
}

// Get user availability
function getAvailability() {
    return data.availability;
}

// Get all FAMs
function getFAMs() {
    return data.fams;
}

// Get available FAMs (with open slots)
function getAvailableFAMs() {
    return data.fams.filter(f => f.isAvailable && f.mentees < f.maxMentees);
}

// Get FAM by ID
function getFAMById(id) {
    return data.fams.find(f => f.id === id);
}

// Get all professors
function getProfessors() {
    return data.professors;
}

// Get professor by ID
function getProfessorById(id) {
    return data.professors.find(p => p.id === id);
}

// Get all students (for peer-to-peer)
function getStudents() {
    return data.students;
}

// Get student by ID
function getStudentById(id) {
    return data.students.find(s => s.id === id);
}

// Get current user
function getCurrentUser() {
    return data.currentUser;
}

// Update current user role
function updateUserRole(role) {
    data.currentUser.role = role;
    return data.currentUser;
}

// Calculate statistics
function getStats() {
    return {
        upcoming: getUpcomingMeetings().length,
        completed: getCompletedMeetings().length,
        total: data.meetings.length,
        cancelledCount: data.meetings.filter(m => m.status === 'Cancelled').length
    };
}

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        data,
        getMeetings,
        getUpcomingMeetings,
        getCompletedMeetings,
        getMeetingById,
        addMeeting,
        cancelMeeting,
        getAvailability,
        getFAMs,
        getAvailableFAMs,
        getFAMById,
        getProfessors,
        getProfessorById,
        getStudents,
        getStudentById,
        getCurrentUser,
        updateUserRole,
        getStats
    };
}
