/**
 * app.js - Main Application Logic
 * Handles UI interactions, event listeners, and application state
 */

// Global state
let currentTab = 'upcoming';
let selectedTimeSlot = null;

/**
 * Authentication helper functions
 */
function isAuthenticated() {
    return localStorage.getItem('isLoggedIn') === 'true';
}

function redirectToLogin() {
    window.location.href = 'login.html';
}

function loadUserFromStorage() {
    const userData = localStorage.getItem('currentUser');
    if (userData) {
        const user = JSON.parse(userData);
        // Ensure we always have a displayable name
        if (!user.name) {
            // Derive a readable name from email if possible
            if (user.email) {
                const local = user.email.split('@')[0] || user.email;
                const pretty = local.replace(/[._-]+/g, ' ').trim();
                user.name = pretty ? capitalizeWords(pretty) : user.email;
            } else {
                user.name = 'User';
            }
        }
        // Normalize role strings (mentor → fam)
        if (user.role === 'mentor') user.role = 'fam';
        // Update the global data object with the logged-in user
        data.currentUser = user;
    }
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userRole');
    redirectToLogin();
}

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    if (!isAuthenticated()) {
        redirectToLogin();
        return;
    }
    
    // Load user data from localStorage
    loadUserFromStorage();
    
    init();
    setupEventListeners();
});

/**
 * Main initialization function
 */
function init() {
    const user = getCurrentUser();
    const role = user.role;
    
    // Show/hide tabs based on role
    setupRoleBasedTabs(role);
    
    renderMeetings();
    renderAvailability();
    if (role === 'student') {
    renderFAMs();
    }
    if (role === 'fam') {
        renderMeetingNotes();
    }
    updateStats();
    setMinDate();
    updateRoleDisplay();
    lucide.createIcons();
}

/**
 * Setup tabs based on user role
 */
function setupRoleBasedTabs(role) {
    const bookTabBtn = document.getElementById('bookTabBtn');
    const famsTabBtn = document.getElementById('famsTabBtn');
    const notesTabBtn = document.getElementById('notesTabBtn');
    
    if (role === 'student') {
        // Students can book meetings and see FAMs
        bookTabBtn.style.display = 'block';
        famsTabBtn.style.display = 'block';
        notesTabBtn.style.display = 'none';
    } else if (role === 'professor') {
        // Professors can only see meetings
        bookTabBtn.style.display = 'none';
        famsTabBtn.style.display = 'none';
        notesTabBtn.style.display = 'none';
    } else if (role === 'fam') {
        // FAMs can see meetings and add notes
        bookTabBtn.style.display = 'none';
        famsTabBtn.style.display = 'none';
        notesTabBtn.style.display = 'block';
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Time slot selection
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('time-slot')) {
            selectTimeSlot(e.target);
        }
    });

    // Modal close on outside click
    document.getElementById('meetingModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
}

/**
 * Set minimum date for date input
 */
function setMinDate() {
    const dateInput = document.getElementById('meetingDate');
    if (dateInput) {
        dateInput.min = getTodayDate();
        dateInput.value = getTodayDate();
    }
}

/**
 * Update stats display
 */
function updateStats() {
    const stats = getStats();
    document.getElementById('upcomingCount').textContent = stats.upcoming;
    document.getElementById('completedCount').textContent = stats.completed;
}

/**
 * Render meetings list
 */
function renderMeetings() {
    const meetingList = document.getElementById('meetingList');
    const upcoming = getUpcomingMeetings();
    
    if (upcoming.length === 0) {
        meetingList.innerHTML = `
            <div class="empty-state">
                <i data-lucide="calendar-x"></i>
                <p>No upcoming meetings</p>
            </div>
        `;
    } else {
        meetingList.innerHTML = upcoming.map(meeting => `
            <div class="meeting-item ${meeting.category === 'Student-FAM' ? 'fam' : ''}" 
                 onclick="showMeetingDetails(${meeting.id})">
                <div class="meeting-header">
                    <div class="meeting-title">${meeting.with}</div>
                    <span class="meeting-badge ${meeting.type.toLowerCase()}">${meeting.type}</span>
                </div>
                <div class="meeting-info">
                    <div class="meeting-time">
                        <i data-lucide="calendar" style="width: 14px; height: 14px;"></i>
                        ${formatDate(meeting.date)} at ${formatTime(meeting.startTime)}
                    </div>
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <i data-lucide="${meeting.type === 'Online' ? 'video' : 'map-pin'}" style="width: 14px; height: 14px;"></i>
                        ${meeting.type === 'Online' ? 'Video Call' : meeting.location}
                    </div>
                    <div style="margin-top: 5px; color: #333;">${truncateText(meeting.purpose, 60)}</div>
                </div>
            </div>
        `).join('');
    }
    lucide.createIcons();
}

/**
 * Render availability slots
 */
function renderAvailability() {
    const grid = document.getElementById('availabilityGrid');
    const availability = getAvailability();
    
    grid.innerHTML = availability.map(slot => `
        <div class="availability-card">
            <div class="availability-day">${slot.day}</div>
            <div class="availability-time">${formatTime(slot.start)} - ${formatTime(slot.end)}</div>
        </div>
    `).join('');
}

/**
 * Render FAMs list
 */
function renderFAMs() {
    const famsList = document.getElementById('famsList');
    const fams = getAvailableFAMs();
    
    if (fams.length === 0) {
        famsList.innerHTML = `
            <div class="empty-state">
                <i data-lucide="users-x"></i>
                <p>No FAMs available at the moment</p>
            </div>
        `;
    } else {
        famsList.innerHTML = fams.map(fam => `
            <div class="fam-card">
                <div class="fam-header">
                    <div>
                        <div class="fam-name">${fam.name}</div>
                        <div class="fam-specialization">${fam.specialization}</div>
                    </div>
                </div>
                <div class="fam-bio">${fam.bio}</div>
                <div class="fam-footer">
                    <span>${fam.mentees}/${fam.maxMentees} mentees</span>
                    <button class="btn btn-secondary" onclick="bookWithFAM(${fam.id})">
                        Book Session
                    </button>
                </div>
            </div>
        `).join('');
    }
    lucide.createIcons();
}

/**
 * Render meeting notes for FAMs
 */
function renderMeetingNotes() {
    const notesList = document.getElementById('meetingNotesList');
    const user = getCurrentUser();
    
    // Get all meetings where this FAM is involved
    const allMeetings = getMeetings('all');
    const famMeetings = allMeetings.filter(m => {
        if (m.category !== 'Student-FAM') return false;
        // Check if the FAM's name matches the meeting "with" field
        return m.with && m.with.toLowerCase().includes(user.name.toLowerCase());
    });
    
    if (famMeetings.length === 0) {
        notesList.innerHTML = `
            <div class="empty-state">
                <i data-lucide="file-text"></i>
                <p>No meetings found. Meeting notes will appear here once you have meetings with students.</p>
            </div>
        `;
    } else {
        notesList.innerHTML = famMeetings.map(meeting => {
            const meetingNotes = getMeetingNotes(meeting.id) || '';
            return `
                <div class="meeting-notes-card">
                    <div class="meeting-notes-header">
                        <div>
                            <div class="meeting-notes-title">Meeting with ${meeting.with}</div>
                            <div class="meeting-notes-date">${formatDate(meeting.date)} at ${formatTime(meeting.startTime)}</div>
                        </div>
                        <button class="btn btn-primary" onclick="openNotesModal(${meeting.id})">
                            <i data-lucide="edit"></i>
                            ${meetingNotes ? 'Edit Notes' : 'Add Notes'}
                        </button>
                    </div>
                    ${meetingNotes ? `
                        <div class="meeting-notes-content">
                            <strong>Notes:</strong>
                            <p>${meetingNotes}</p>
                        </div>
                    ` : '<p style="color: var(--text-lighter); font-style: italic;">No notes added yet</p>'}
                </div>
            `;
        }).join('');
    }
    lucide.createIcons();
}

/**
 * Get meeting notes from storage
 */
function getMeetingNotes(meetingId) {
    const notes = JSON.parse(localStorage.getItem('meetingNotes') || '{}');
    return notes[meetingId] || '';
}

/**
 * Save meeting notes to storage
 */
function saveMeetingNotes(meetingId, notes) {
    const allNotes = JSON.parse(localStorage.getItem('meetingNotes') || '{}');
    allNotes[meetingId] = notes;
    localStorage.setItem('meetingNotes', JSON.stringify(allNotes));
}

/**
 * Open notes modal for a meeting
 */
function openNotesModal(meetingId) {
    const meeting = getMeetingById(meetingId);
    if (!meeting) return;
    
    const existingNotes = getMeetingNotes(meetingId);
    
    const modal = document.getElementById('meetingModal');
    const details = document.getElementById('meetingDetails');
    
    details.innerHTML = `
        <div class="meeting-detail-item">
            <strong>Meeting with:</strong> ${meeting.with}
        </div>
        <div class="meeting-detail-item">
            <strong>Date:</strong> ${formatDate(meeting.date)}
        </div>
        <div class="meeting-detail-item">
            <strong>Time:</strong> ${formatTime(meeting.startTime)} - ${formatTime(meeting.endTime)}
        </div>
        <div class="meeting-detail-item">
            <strong>Purpose:</strong> ${meeting.purpose}
        </div>
        <div class="form-group" style="margin-top: 20px;">
            <label for="meetingNotesText">Meeting Notes</label>
            <textarea id="meetingNotesText" rows="8" placeholder="Enter meeting notes here...">${existingNotes}</textarea>
            <small class="form-hint">Document important points discussed, student progress, and any follow-up actions needed.</small>
        </div>
        <div style="margin-top: 20px; display: flex; gap: 10px;">
            <button class="btn btn-primary" onclick="saveNotes(${meetingId})">
                <i data-lucide="save"></i>
                Save Notes
            </button>
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `;
    
    modal.classList.add('active');
    lucide.createIcons();
}

/**
 * Save notes for a meeting
 */
function saveNotes(meetingId) {
    const notes = document.getElementById('meetingNotesText').value.trim();
    saveMeetingNotes(meetingId, notes);
    showNotification('Meeting notes saved successfully!', 'success');
    renderMeetingNotes();
    closeModal();
}

/**
 * Switch between tabs
 */
function switchTab(tabName, buttonElement) {
    currentTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    if (buttonElement) {
        buttonElement.classList.add('active');
    }
    
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Show selected tab
    if (tabName === 'upcoming') {
        document.getElementById('upcomingTab').style.display = 'block';
        renderMeetings();
    } else if (tabName === 'book') {
        document.getElementById('bookTab').style.display = 'block';
        generateTimeSlotsForDate();
    } else if (tabName === 'fams') {
        document.getElementById('famsTab').style.display = 'block';
        renderFAMs();
    } else if (tabName === 'notes') {
        document.getElementById('notesTab').style.display = 'block';
        renderMeetingNotes();
    }
}

// Removed switchRole function - users are logged in with a specific role

/**
 * Update role display in header
 */
function updateRoleDisplay() {
    const badge = document.getElementById('userBadge');
    if (!badge) return;
    
    // Get user data from localStorage
    const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const registeredUsers = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
    
    // Find the registered user to get email
    let userEmail = storedUser.email;
    if (!userEmail && storedUser.role) {
        const regUser = registeredUsers.find(u => u.role === storedUser.role);
        if (regUser) userEmail = regUser.email;
    }
    
    // Get display name
    let displayName = storedUser.name || userEmail || 'User';
    if (displayName.includes('@')) {
        const localPart = displayName.split('@')[0];
        displayName = localPart.replace(/[._-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // Get role
    const role = storedUser.role || 'user';
    const roleDisplay = role === 'fam' || role === 'mentor' ? 'FAM Mentor' : 
                       role === 'professor' ? 'Professor' : 
                       role === 'student' ? 'Student' : 
                       capitalizeWords(role);
    
    badge.textContent = `${displayName} (${roleDisplay})`;
}

/**
 * Select time slot for booking
 */
function selectTimeSlot(element) {
    // Remove previous selection
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
    });
    
    // Add selection to clicked slot
    element.classList.add('selected');
    selectedTimeSlot = element.dataset.time;
}

/**
 * Show meeting details in modal
 */
function showMeetingDetails(meetingId) {
    const meeting = getMeetingById(meetingId);
    if (!meeting) return;
    
    const user = getCurrentUser();
    const isFAM = user.role === 'fam';
    const isFAMMeeting = meeting.category === 'Student-FAM';
    const existingNotes = isFAM ? getMeetingNotes(meetingId) : '';
    
    const modal = document.getElementById('meetingModal');
    const details = document.getElementById('meetingDetails');
    
    details.innerHTML = `
        <div class="meeting-detail-item">
            <strong>With:</strong> ${meeting.with}
        </div>
        <div class="meeting-detail-item">
            <strong>Date:</strong> ${formatDate(meeting.date)}
        </div>
        <div class="meeting-detail-item">
            <strong>Time:</strong> ${formatTime(meeting.startTime)} - ${formatTime(meeting.endTime)}
        </div>
        <div class="meeting-detail-item">
            <strong>Type:</strong> ${meeting.type}
        </div>
        <div class="meeting-detail-item">
            <strong>Purpose:</strong> ${meeting.purpose}
        </div>
        ${meeting.location ? `<div class="meeting-detail-item"><strong>Location:</strong> ${meeting.location}</div>` : ''}
        ${meeting.link ? `<div class="meeting-detail-item"><strong>Meeting Link:</strong> <a href="${meeting.link}" target="_blank">${meeting.link}</a></div>` : ''}
        ${meeting.feedback ? `<div class="meeting-detail-item"><strong>Feedback:</strong> ${meeting.feedback}</div>` : ''}
        ${isFAM && isFAMMeeting && existingNotes ? `
            <div class="meeting-detail-item" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);">
                <strong>Meeting Notes:</strong>
                <p style="margin-top: 10px; white-space: pre-wrap;">${existingNotes}</p>
            </div>
        ` : ''}
        <div style="margin-top: 20px; display: flex; gap: 10px;">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
            ${isFAM && isFAMMeeting ? `<button class="btn btn-primary" onclick="openNotesModal(${meeting.id})">
                <i data-lucide="edit"></i>
                ${existingNotes ? 'Edit Notes' : 'Add Notes'}
            </button>` : ''}
            ${meeting.status === 'Scheduled' && !isFAM ? `<button class="btn btn-primary" onclick="handleCancelMeeting(${meeting.id})">Cancel Meeting</button>` : ''}
        </div>
    `;
    
    modal.classList.add('active');
    lucide.createIcons();
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('meetingModal').classList.remove('active');
}

/**
 * Book meeting with FAM
 */
function bookWithFAM(famId) {
    const fam = getFAMById(famId);
    if (!fam) return;
    
    // Switch to book tab and pre-fill FAM selection
    switchTab('book');
    
    // Pre-select FAM meeting type and person
    document.getElementById('meetingType').value = 'Student-FAM';
    populateMeetingWithOptions();
    document.getElementById('meetingWith').value = famId;
    
    // Scroll to form
    document.getElementById('bookTab').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Cancel meeting
 */
function handleCancelMeeting(meetingId) {
    if (confirmAction('Are you sure you want to cancel this meeting?')) {
        const success = cancelMeeting(meetingId);
        if (success) {
            showNotification('Meeting cancelled successfully', 'success');
            renderMeetings();
            updateStats();
            closeModal();
        } else {
            showNotification('Failed to cancel meeting', 'error');
        }
    }
}

/**
 * Handle meeting form submission
 */
function handleMeetingFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const meetingData = {
        category: document.getElementById('meetingType').value,
        with: document.getElementById('meetingWith').selectedOptions[0].text,
        date: document.getElementById('meetingDate').value,
        startTime: selectedTimeSlot,
        endTime: getEndTime(selectedTimeSlot),
        type: 'Online', // Default to online for now
        purpose: document.getElementById('meetingPurpose').value,
        link: 'https://meet.google.com/meet-' + Math.random().toString(36).substring(7)
    };
    
    // Basic validation
    if (!meetingData.category) {
        showNotification('Please choose a meeting type', 'error');
        return;
    }
    if (!document.getElementById('meetingWith').value) {
        showNotification('Please choose who you are meeting', 'error');
        return;
    }
    if (!meetingData.date) {
        showNotification('Please choose a date', 'error');
        return;
    }
    if (!selectedTimeSlot) {
        showNotification('Please select a time slot', 'error');
        return;
    }
    
    const newMeeting = addMeeting(meetingData);
    if (newMeeting) {
        showNotification('Meeting booked successfully!', 'success');
        renderMeetings();
        updateStats();
        resetMeetingForm();
    } else {
        showNotification('Failed to book meeting', 'error');
    }
}

/**
 * Reset meeting form
 */
function resetMeetingForm() {
    document.getElementById('meetingForm').reset();
    selectedTimeSlot = null;
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
    });
    setMinDate();
}

/**
 * Get end time (30 minutes after start)
 */
function getEndTime(startTime) {
    const [hours, minutes] = startTime.split(':').map(Number);
    const totalMinutes = hours * 60 + minutes + 30;
    const endHours = Math.floor(totalMinutes / 60);
    const endMinutes = totalMinutes % 60;
    return `${String(endHours).padStart(2, '0')}:${String(endMinutes).padStart(2, '0')}`;
}

/**
 * Populate meeting "with" options based on meeting type
 */
function populateMeetingWithOptions() {
    const meetingType = document.getElementById('meetingType').value;
    const meetingWithSelect = document.getElementById('meetingWith');
    
    meetingWithSelect.innerHTML = '<option value="">Select person</option>';
    
    if (meetingType === 'Student-Professor') {
        const professors = getProfessors();
        professors.forEach(prof => {
            const option = document.createElement('option');
            option.value = prof.id;
            option.textContent = prof.name;
            meetingWithSelect.appendChild(option);
        });
    } else if (meetingType === 'Student-FAM') {
        const fams = getAvailableFAMs();
        fams.forEach(fam => {
            const option = document.createElement('option');
            option.value = fam.id;
            option.textContent = fam.name;
            meetingWithSelect.appendChild(option);
        });
    }
    
    // Generate time slots for the selected date
    generateTimeSlotsForDate();
}

/**
 * Generate time slots for selected date
 */
function generateTimeSlotsForDate() {
    const timeSlotsContainer = document.getElementById('timeSlots');
    const availability = getAvailability();
    
    // For simplicity, generate common time slots
    const commonSlots = [
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
    ];
    
    timeSlotsContainer.innerHTML = commonSlots.map(time => `
        <div class="time-slot" data-time="${time}">
            ${formatTime(time)}
        </div>
    `).join('');
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Meeting form submission
    const meetingForm = document.getElementById('meetingForm');
    if (meetingForm) {
        meetingForm.addEventListener('submit', handleMeetingFormSubmit);
    }
    
    // Meeting type change
    const meetingTypeSelect = document.getElementById('meetingType');
    if (meetingTypeSelect) {
        meetingTypeSelect.addEventListener('change', populateMeetingWithOptions);
    }
    
    // Meeting date change
    const meetingDateInput = document.getElementById('meetingDate');
    if (meetingDateInput) {
        meetingDateInput.addEventListener('change', generateTimeSlotsForDate);
    }
});
