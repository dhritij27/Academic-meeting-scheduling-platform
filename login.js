/**
 * login.js - Login Page Functionality
 * Handles user authentication with email, password, and role
 */

/**
 * Initialize login page
 */
document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();
    if (localStorage.getItem('isLoggedIn') === 'true') {
        window.location.href = 'index.html';
        return;
    }
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

/**
 * Handle login form submission
 */
function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value.trim().toLowerCase();
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    if (!email || !password || !role) return showNotification('Please fill all fields', 'error');
    const user = getStoredUser(email, password, role);
    if (!user) return showNotification('Invalid credentials or role!', 'error');
    
    // Store user with email for display
    const userData = {
        email: email,
        role: role,
        name: email.split('@')[0].replace(/[._-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    };
    
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('currentUser', JSON.stringify(userData));
    localStorage.setItem('userRole', role);
    showNotification('Login successful!', 'success');
    setTimeout(()=>window.location='index.html',700);
}

function getStoredUser(email, password, role) {
    const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
    return users.find(u => u.email === email && u.password === password && u.role === role);
}

// showNotification is defined in utility.js

/**
 * Redirect to dashboard
 */
function redirectToDashboard() {
    window.location.href = 'index.html';
}

/**
 * Logout function (can be called from dashboard)
 */
function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userRole');
    window.location.href = 'login.html';
}
