/**
 * utils.js - Utility Functions
 * Helper functions for formatting, validation, and common operations
 */

/**
 * Format date from YYYY-MM-DD to readable format
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { weekday: 'short', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Format time from 24h to 12h format
 * @param {string} timeString - Time in HH:MM format
 * @returns {string} Formatted time string
 */
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

/**
 * Get day of week from date string
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @returns {string} Day of week
 */
function getDayOfWeek(dateString) {
    const date = new Date(dateString);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
}

/**
 * Check if a date is in the past
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @returns {boolean}
 */
function isPastDate(dateString) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const checkDate = new Date(dateString);
    return checkDate < today;
}

/**
 * Get today's date in YYYY-MM-DD format
 * @returns {string}
 */
function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

/**
 * Generate time slots between start and end time
 * @param {string} startTime - Start time in HH:MM format
 * @param {string} endTime - End time in HH:MM format
 * @param {number} intervalMinutes - Interval between slots
 * @returns {Array} Array of time slot objects
 */
function generateTimeSlots(startTime, endTime, intervalMinutes = 30) {
    const slots = [];
    const [startHour, startMin] = startTime.split(':').map(Number);
    const [endHour, endMin] = endTime.split(':').map(Number);
    
    let currentTime = startHour * 60 + startMin;
    const endTimeMinutes = endHour * 60 + endMin;
    
    while (currentTime + intervalMinutes <= endTimeMinutes) {
        const slotStartHour = Math.floor(currentTime / 60);
        const slotStartMin = currentTime % 60;
        const slotEndTime = currentTime + intervalMinutes;
        const slotEndHour = Math.floor(slotEndTime / 60);
        const slotEndMin = slotEndTime % 60;
        
        const start = `${String(slotStartHour).padStart(2, '0')}:${String(slotStartMin).padStart(2, '0')}`;
        const end = `${String(slotEndHour).padStart(2, '0')}:${String(slotEndMin).padStart(2, '0')}`;
        
        slots.push({
            start,
            end,
            display: `${formatTime(start)} - ${formatTime(end)}`
        });
        
        currentTime += intervalMinutes;
    }
    
    return slots;
}

/**
 * Validate email format
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number format (Indian)
 * @param {string} phone
 * @returns {boolean}
 */
function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
    return phoneRegex.test(phone);
}

/**
 * Truncate text to specified length
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Capitalize first letter of each word
 * @param {string} str
 * @returns {string}
 */
function capitalizeWords(str) {
    return str.replace(/\b\w/g, char => char.toUpperCase());
}

/**
 * Get initials from name
 * @param {string} name
 * @returns {string}
 */
function getInitials(name) {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
}

/**
 * Sort array of objects by property
 * @param {Array} array
 * @param {string} property
 * @param {string} order - 'asc' or 'desc'
 * @returns {Array}
 */
function sortBy(array, property, order = 'asc') {
    return array.sort((a, b) => {
        if (order === 'asc') {
            return a[property] > b[property] ? 1 : -1;
        } else {
            return a[property] < b[property] ? 1 : -1;
        }
    });
}

/**
 * Filter array by search term
 * @param {Array} array
 * @param {string} searchTerm
 * @param {Array} properties - Properties to search in
 * @returns {Array}
 */
function filterBySearch(array, searchTerm, properties) {
    if (!searchTerm) return array;
    
    searchTerm = searchTerm.toLowerCase();
    return array.filter(item => {
        return properties.some(prop => {
            const value = item[prop];
            return value && value.toString().toLowerCase().includes(searchTerm);
        });
    });
}

/**
 * Generate random ID
 * @returns {string}
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

/**
 * Deep clone object
 * @param {Object} obj
 * @returns {Object}
 */
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Debounce function
 * @param {Function} func
 * @param {number} wait
 * @returns {Function}
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show notification/toast message
 * @param {string} message
 * @param {string} type - 'success', 'error', 'info', 'warning'
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : type === 'warning' ? '#f59e0b' : '#667eea'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Confirm dialog
 * @param {string} message
 * @returns {boolean}
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Format rating as stars
 * @param {number} rating
 * @returns {string}
 */
function formatRating(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = '⭐'.repeat(fullStars);
    if (hasHalfStar) stars += '⭐';
    return stars;
}

/**
 * Calculate time difference in minutes
 * @param {string} startTime - HH:MM format
 * @param {string} endTime - HH:MM format
 * @returns {number}
 */
function getTimeDifferenceMinutes(startTime, endTime) {
    const [startHour, startMin] = startTime.split(':').map(Number);
    const [endHour, endMin] = endTime.split(':').map(Number);
    
    const startMinutes = startHour * 60 + startMin;
    const endMinutes = endHour * 60 + endMin;
    
    return endMinutes - startMinutes;
}

/**
 * Check if time slot is available (no conflicts)
 * @param {Array} meetings - Array of meeting objects
 * @param {string} date - YYYY-MM-DD format
 * @param {string} startTime - HH:MM format
 * @param {string} endTime - HH:MM format
 * @returns {boolean}
 */
function isTimeSlotAvailable(meetings, date, startTime, endTime) {
    return !meetings.some(meeting => {
        if (meeting.date !== date || meeting.status === 'Cancelled') {
            return false;
        }
        
        // Check for time overlap
        return (startTime < meeting.endTime && endTime > meeting.startTime);
    });
}

/**
 * Export functions if using modules
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatDate,
        formatTime,
        getDayOfWeek,
        isPastDate,
        getTodayDate,
        generateTimeSlots,
        isValidEmail,
        isValidPhone,
        truncateText,
        capitalizeWords,
        getInitials,
        sortBy,
        filterBySearch,
        generateId,
        deepClone,
        debounce,
        showNotification,
        confirmAction,
        formatRating,
        getTimeDifferenceMinutes,
        isTimeSlotAvailable
    };
}
