/**
 * app.js - Main Application Logic
 * Handles UI interactions, event listeners, and application state
 */

// Global state
let currentTab = 'upcoming';
let selectedTimeSlot = null;

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    init();
    setupEventListeners();
});

/**
 * Main initialization function
 */
function init() {
    renderMeetings();
    renderAvailability();
    renderFAMs();
    updateStats();
    setMinDate();
    updateRoleDisplay();
    lucide.createIcons();
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
            <div class="meeting-item ${meeting.category === 'Student-FAM' ? 'fam' : meeting.category === 'Peer-to-Peer' ? 'peer' : ''}" 
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
                    <div class="rating">
                        <i data-lucide="star" style="width: 14px; height: 14px; fill: white;"></i>
                        ${fam.rating.toFixed(2)}
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
 * Switch between tabs
 */
function switchTab(tabName) {
    currentTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Show selected tab
    if (tabName === 'upcoming') {
        document.getElementById('upcomingTab').style.display = 'block';
    } else if (tabName === 'book') {
        document.getElementById('bookTab').style.display = 'block';
    } else if (tabName === 'fams') {
        document.getElementById('famsTab').style.display = 'block';
    }
}

/**
 * Switch user role
 */
function switchRole(role) {
    updateUserRole(role);
    
    // Update role buttons
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update user badge
    updateRoleDisplay();
    
    // Show/hide FAM tab based on role
    const famsTab
