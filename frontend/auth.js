/**
 * HealthBridge | Authentication Logic (Responsive + Full API Integration)
 * Preserves all original endpoints and validation rules.
 */

let currentRole = 'patient';

function setRole(role) {
    currentRole = role;
    document.querySelectorAll('.role-option').forEach(opt => opt.classList.remove('active'));
    const selectedRole = document.querySelector(`[data-role="${role}"]`);
    if (selectedRole) selectedRole.classList.add('active');

    const deptField = document.getElementById('deptField');
    if (deptField) {
        const isSignup = document.getElementById('submitBtn').innerText === "Sign Up";
        deptField.classList.toggle('hidden', role !== 'doctor' || !isSignup);
    }
}

function showMode(mode) {
    const isSignup = mode === 'signup';

    // Toggle button active states
    document.getElementById('toggleSignin').classList.toggle('active', !isSignup);
    document.getElementById('toggleSignup').classList.toggle('active', isSignup);

    // Update texts
    document.getElementById('formTitle').innerText = isSignup ? "Create Account" : "Access Portal";
    document.getElementById('submitBtn').innerText = isSignup ? "Sign Up" : "Sign In";

    // Toggle visibility of signup-specific fields
    const toggleFields = ['roleSelection', 'nameField', 'contactSection', 'bloodGroupField'];
    toggleFields.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.toggle('hidden', !isSignup);
    });

    // Department field (only for doctors during signup)
    const deptField = document.getElementById('deptField');
    if (deptField) {
        deptField.classList.toggle('hidden', !isSignup || currentRole !== 'doctor');
    }

    // Clear any previous messages
    const msgBox = document.getElementById('messageBox');
    if (msgBox) msgBox.classList.add('hidden');
}

// Handle form submission
document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const mode = document.getElementById('submitBtn').innerText; // "Sign Up" or "Sign In"
    const emailInput = document.getElementById('userEmail');
    const phoneInput = document.getElementById('userPhone');
    const email = emailInput ? emailInput.value.trim() : "";
    const phone = phoneInput ? phoneInput.value.trim() : "";

    // Validation: for Sign Up, at least email OR phone is required
    if (mode === "Sign Up" && !email && !phone) {
        alert("Institutional records require either an Email Address or a Phone Number.");
        return;
    }

    const userId = document.getElementById('userId').value.trim();
    if (!userId) {
        alert("Institutional ID is required.");
        return;
    }

    const data = {
        user_id: userId,
        name: document.getElementById('userName').value.trim() || "User",
        email: email || null,
        phone: phone || null,
        role: currentRole,
        password: "password123",   // as per original design
        dept: currentRole === 'doctor' ? document.getElementById('department').value.trim() : null,
        blood_group: document.getElementById('bloodGroup').value || null
    };

    const endpoint = mode.trim().toLowerCase() === "sign up" ? "signup" : "login";

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Store user info for session
            localStorage.setItem('userId', result.user_id || data.user_id);
            localStorage.setItem('userName', result.name || data.name);
            localStorage.setItem('userRole', result.role || data.role);
            // Redirect to dashboard (ensure dashboard.html exists)
            window.location.href = 'dashboard.html';
        } else {
            // Display backend error
            const errorMsg = result.detail || "Authentication failed. Please check credentials.";
            const msgBox = document.getElementById('messageBox');
            if (msgBox) {
                msgBox.innerText = errorMsg;
                msgBox.classList.remove('hidden');
            } else {
                alert(errorMsg);
            }
        }
    } catch (err) {
        console.error(err);
        alert("Network error: Cannot reach the authentication server. Make sure FastAPI is running on http://127.0.0.1:8000");
    }
});

// Initial UI setup (default: signin mode)
showMode('signin');
setRole('patient');