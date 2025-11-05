/**
 * signup.js - Sign Up Page Functionality
 * Handles student registration with SRN and password
 */

/**
 * Initialize signup page
 */
document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons();
    
    // Check if user is already logged in
    if (localStorage.getItem('isLoggedIn') === 'true') {
        redirectToDashboard();
        return;
    }
    
    setupEventListeners();
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

    // SRN format validation
    const srnInput = document.getElementById('srn');
    if (srnInput) {
        srnInput.addEventListener('input', function() {
            const srn = this.value.toUpperCase();
            this.value = srn;
        });
    }
}

/**
 * Validate password match in real-time
 */
function validatePasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorMessage = document.getElementById('passwordMatch');
    
    if (confirmPassword.length > 0) {
        if (password !== confirmPassword) {
            errorMessage.style.display = 'block';
            errorMessage.style.color = '#ef4444';
            return false;
        } else {
            errorMessage.style.display = 'none';
            return true;
        }
    } else {
        errorMessage.style.display = 'none';
        return true;
    }
}

/**
 * Validate SRN format
 */
function validateSRN(srn) {
    const srnPattern = /^SRN[0-9]{7}$/;
    return srnPattern.test(srn.toUpperCase());
}

/**
 * Handle signup form submission
 */
function handleSignup(event) {
    event.preventDefault();
    
    const srn = document.getElementById('srn').value.trim().toUpperCase();
    const name = document.getElementById('name').value.trim();
    const department = document.getElementById('department').value;
    const year = parseInt(document.getElementById('year').value);
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validate all fields
    if (!srn || !name || !department || !year || !password || !confirmPassword) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    // Validate SRN format
    if (!validateSRN(srn)) {
        showNotification('Invalid SRN format. Please use format: SRN followed by 7 digits (e.g., SRN2024001)', 'error');
        return;
    }
    
    // Validate password match
    if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        showNotification('Password must be at least 6 characters long', 'error');
        return;
    }
    
    // Check if SRN already exists
    if (isSRNAlreadyRegistered(srn)) {
        showNotification('This SRN is already registered. Please sign in instead.', 'error');
        return;
    }
    
    // Create new student account
    const newStudent = createStudentAccount({
        srn: srn,
        name: name,
        department: department,
        year: year,
        password: password
    });
    
    if (newStudent) {
        showNotification('Account created successfully! Redirecting to login...', 'success');
        
        // Store registration info temporarily
        localStorage.setItem('newStudent', JSON.stringify(newStudent));
        
        // Redirect to login after a short delay
        setTimeout(() => {
            window.location.href = 'login.html?srn=' + encodeURIComponent(srn);
        }, 1500);
    } else {
        showNotification('Failed to create account. Please try again.', 'error');
    }
}

/**
 * Check if SRN is already registered
 */
function isSRNAlreadyRegistered(srn) {
    const students = getStudents();
    const existingStudent = students.find(s => s.srn.toUpperCase() === srn.toUpperCase());
    return !!existingStudent;
}

/**
 * Create new student account
 */
function createStudentAccount(studentData) {
    try {
        // Generate new student ID
        const students = getStudents();
        const newId = Math.max(...students.map(s => s.id), 0) + 1;
        
        // Create student object
        const newStudent = {
            id: newId,
            name: studentData.name,
            srn: studentData.srn.toUpperCase(),
            department: studentData.department,
            year: studentData.year,
            password: studentData.password // In production, this should be hashed
        };
        
        // Add to students data (in production, this would be an API call)
        students.push(newStudent);
        
        // Store in localStorage for demo purposes
        // In production, this would be handled by the backend
        const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
        users.push({
            srn: newStudent.srn,
            password: newStudent.password,
            role: 'student',
            user: newStudent
        });
        localStorage.setItem('registeredUsers', JSON.stringify(users));
        
        return newStudent;
    } catch (error) {
        console.error('Error creating student account:', error);
        return null;
    }
}

/**
 * Redirect to dashboard
 */
function redirectToDashboard() {
    window.location.href = 'index.html';
}
