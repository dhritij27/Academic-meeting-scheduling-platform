/**
 * signup.js - Sign Up Page Functionality
 * Handles student registration with SRN and password
 */

/**
 * Initialize signup page
 */
document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();
    if (localStorage.getItem('isLoggedIn') === 'true') {
        window.location.href = 'index.html'; return;
    }
    document.getElementById('signupForm').addEventListener('submit', handleSignup);
    document.getElementById('confirmPassword').addEventListener('input', validatePasswordMatch);
    document.getElementById('password').addEventListener('input', validatePasswordMatch);
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }

    // Real-time password confirmation validation
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('input', validatePasswordMatch);
    }
}

/**
 * Validate password match in real-time
 */
function validatePasswordMatch() {
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirmPassword').value;
    const errorMsg = document.getElementById('passwordMatch');
    if (confirm && password !== confirm) { errorMsg.style.display = 'block'; return false; }
    else { errorMsg.style.display = 'none'; return true; }
}

/**
 * Handle signup form submission
 */
function handleSignup(e) {
    e.preventDefault();
    const email = document.getElementById('email').value.trim().toLowerCase();
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('confirmPassword').value;
    const role = document.getElementById('role').value;
    if (!email || !password || !confirm || !role) return showNotification('Please fill all fields','error');
    if (!validateEmail(email)) return showNotification('Invalid email!','error');
    if (password.length < 6) return showNotification('Password too short','error');
    if (password !== confirm) return showNotification('Passwords do not match','error');
    if (isEmailRegistered(email, role)) return showNotification('Email/role already registered.','error');
    storeUser({email, password, role});
    showNotification('Registration successful! Redirecting...', 'success');
    setTimeout(()=>window.location='login.html',1200);
}


/**
 * Redirect to dashboard
 */
function redirectToDashboard() {
    window.location.href = 'index.html';
}

function validateEmail(email) {
    return /^[^@]+@[^@]+\.[^@]+$/.test(email);
}
function isEmailRegistered(email, role) {
    const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
    return users.some(u => u.email === email && u.role === role);
}
function storeUser(user) {
    const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
    users.push(user);
    localStorage.setItem('registeredUsers', JSON.stringify(users));
}
function showNotification(msg, type) {
    alert(msg);
}

