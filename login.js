/**
 * login.js - Login Page Functionality
 * Handles user authentication and role selection
 */

let selectedRole = null;

/**
 * Initialize login page
 */
document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();
    
    // Check if user is already logged in
    if (localStorage.getItem('isLoggedIn') === 'true') {
        redirectToDashboard();
        return;
    }
    
    setupEventListeners();
    
    // Check if redirected from signup with SRN parameter
    const urlParams = new URLSearchParams(window.location.search);
    const srn = urlParams.get('srn');
    if (srn) {
        // Auto-select student role and pre-fill SRN
        selectRole('student');
        document.getElementById('srnOrUsername').value = srn;
        showNotification('Account created successfully! Please sign in with your password.', 'success');
    }
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
}

/**
 * Select user role
 */
function selectRole(role) {
    selectedRole = role;
    
    // Update visual selection
    document.querySelectorAll('.role-option').forEach(option => {
        option.classList.remove('selected');
    });
    document.querySelector(`[data-role="${role}"]`).classList.add('selected');
    
    // Show login form and footer
    document.getElementById('loginForm').style.display = 'block';
    document.querySelector('.login-footer').style.display = 'block';
    document.querySelector('.demo-credentials').style.display = 'block';
    document.querySelector('.back-btn').style.display = 'block';
    
    // Update form label and placeholder based on role
    const loginLabel = document.getElementById('loginLabel');
    const srnOrUsernameInput = document.getElementById('srnOrUsername');
    // Defensive: if elements aren't yet available in the DOM, bail out gracefully
    if (!loginLabel || !srnOrUsernameInput) {
        console.warn('Login input elements not found. Ensure login.html is updated.');
        return;
    }
    
    if (role === 'student') {
        loginLabel.textContent = 'SRN';
        srnOrUsernameInput.placeholder = 'Enter your SRN (e.g., SRN2024001)';
        srnOrUsernameInput.pattern = '[A-Z]{3}[0-9]{7}';
    } else if (role === 'professor') {
        loginLabel.textContent = 'Username / Staff ID';
        srnOrUsernameInput.placeholder = 'Enter your username or staff ID';
        srnOrUsernameInput.removeAttribute('pattern');
    } else if (role === 'fam') {
        loginLabel.textContent = 'Username / SRN';
        srnOrUsernameInput.placeholder = 'Enter your username or SRN';
        srnOrUsernameInput.removeAttribute('pattern');
    }
    
    // Convert SRN to uppercase for students
    if (role === 'student') {
        srnOrUsernameInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
}

/**
 * Go back to role selection
 */
function goBack() {
    selectedRole = null;
    
    // Hide login form
    document.getElementById('loginForm').style.display = 'none';
    document.querySelector('.login-footer').style.display = 'none';
    document.querySelector('.demo-credentials').style.display = 'none';
    document.querySelector('.back-btn').style.display = 'none';
    
    // Remove selection
    document.querySelectorAll('.role-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Clear form
    document.getElementById('loginForm').reset();
}

/**
 * Handle login form submission
 */
function handleLogin(event) {
    event.preventDefault();
    // Read inputs defensively
    const srnOrUsernameEl = document.getElementById('srnOrUsername');
    const passwordEl = document.getElementById('password');
    if (!srnOrUsernameEl || !passwordEl) {
        showNotification('Login form is not ready. Please refresh the page.', 'error');
        return;
    }
    const srnOrUsername = srnOrUsernameEl.value.trim().toUpperCase();
    const password = passwordEl.value.trim();
    
    if (!srnOrUsername || !password) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    // Authenticate user
    const user = authenticateUser(srnOrUsername, password, selectedRole);
    
    if (user) {
        // Store login state
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('currentUser', JSON.stringify(user));
        localStorage.setItem('userRole', selectedRole);
        
        showNotification(`Welcome back, ${user.name}!`, 'success');
        
        // Redirect to dashboard after a short delay
        setTimeout(() => {
            redirectToDashboard();
        }, 1000);
    } else {
        showNotification('Invalid credentials. Please try again.', 'error');
    }
}

/**
 * Authenticate user based on credentials
 */
function authenticateUser(srnOrUsername, password, role) {
    // First, check registered users from localStorage (for students who signed up)
    if (role === 'student') {
        const registeredUsers = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
        const registeredUser = registeredUsers.find(user => 
            user.srn.toUpperCase() === srnOrUsername.toUpperCase() && 
            user.password === password && 
            user.role === role
        );
        
        if (registeredUser) {
            return registeredUser.user;
        }
    }
    
    // Then check against existing credentials
    const credentials = getLoginCredentials();
    
    for (const cred of credentials) {
        // For students, check by SRN
        if (role === 'student') {
            if (cred.user.srn && cred.user.srn.toUpperCase() === srnOrUsername.toUpperCase() && 
                cred.password === password && 
                cred.role === role) {
                return cred.user;
            }
            // Also check by username for backward compatibility
            if (cred.username.toLowerCase() === srnOrUsername.toLowerCase() && 
                cred.password === password && 
                cred.role === role) {
                return cred.user;
            }
        } else if (role === 'professor') {
            // For professors, check by username or staff ID
            if (cred.username.toLowerCase() === srnOrUsername.toLowerCase() && 
                cred.password === password && 
                cred.role === role) {
                return cred.user;
            }
            // Also check by staff ID
            if (cred.user.staffId && cred.user.staffId.toUpperCase() === srnOrUsername.toUpperCase() && 
                cred.password === password && 
                cred.role === role) {
                return cred.user;
            }
        } else if (role === 'fam') {
            // For FAMs, check by username or SRN
            if (cred.username.toLowerCase() === srnOrUsername.toLowerCase() && 
                cred.password === password && 
                cred.role === role) {
                return cred.user;
            }
            // Also check by SRN
            if (cred.user.srn && cred.user.srn.toUpperCase() === srnOrUsername.toUpperCase() && 
                cred.password === password && 
                cred.role === role) {
                return cred.user;
            }
        }
    }
    
    return null;
}

/**
 * Get login credentials from data
 */
function getLoginCredentials() {
    return [
        // Student credentials
        {
            username: 'student1',
            password: 'password123',
            role: 'student',
            user: {
                role: 'student',
                id: 13,
                name: 'Meera Iyer',
                srn: 'SRN2024001',
                department: 'Computer Science',
                year: 1
            }
        },
        {
            username: 'student2',
            password: 'password123',
            role: 'student',
            user: {
                role: 'student',
                id: 17,
                name: 'Aisha Patel',
                srn: 'SRN2024005',
                department: 'Computer Science',
                year: 1
            }
        },
        {
            username: 'student3',
            password: 'password123',
            role: 'student',
            user: {
                role: 'student',
                id: 18,
                name: 'Dev Sharma',
                srn: 'SRN2024006',
                department: 'Computer Science',
                year: 1
            }
        },
        
        // Professor credentials
        {
            username: 'prof1',
            password: 'professor123',
            role: 'professor',
            user: {
                role: 'professor',
                id: 1,
                name: 'Dr. Rajesh Kumar',
                staffId: 'PROF001',
                department: 'Computer Science',
                courses: ['Data Structures and Algorithms'],
                officeLocation: 'Block A, Room 301',
                email: 'rajesh.kumar@university.edu',
                phone: '+91-9876543210'
            }
        },
        {
            username: 'prof2',
            password: 'professor123',
            role: 'professor',
            user: {
                role: 'professor',
                id: 2,
                name: 'Dr. Priya Sharma',
                staffId: 'PROF002',
                department: 'Computer Science',
                courses: ['Database Management Systems'],
                officeLocation: 'Block A, Room 305',
                email: 'priya.sharma@university.edu',
                phone: '+91-9876543211'
            }
        },
        {
            username: 'prof3',
            password: 'professor123',
            role: 'professor',
            user: {
                role: 'professor',
                id: 5,
                name: 'Dr. Suresh Patel',
                staffId: 'PROF005',
                department: 'Computer Science',
                courses: ['Machine Learning'],
                officeLocation: 'Block A, Room 310',
                email: 'suresh.patel@university.edu',
                phone: '+91-9876543214'
            }
        },
        
        // FAM credentials
        {
            username: 'fam1',
            password: 'mentor123',
            role: 'fam',
            user: {
                role: 'fam',
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
            }
        },
        {
            username: 'fam2',
            password: 'mentor123',
            role: 'fam',
            user: {
                role: 'fam',
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
            }
        },
        {
            username: 'fam3',
            password: 'mentor123',
            role: 'fam',
            user: {
                role: 'fam',
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
            }
        }
    ];
}

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
