// Function to toggle password visibility
function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const toggleIcon = document.querySelector(`.toggle-${fieldId}`);

    // Toggle the password field type
    if (passwordField.type === "password") {
        passwordField.type = "text"; // Show password
        toggleIcon.classList.remove("bx-show");
        toggleIcon.classList.add("bx-hide");
    } else {
        passwordField.type = "password"; // Hide password
        toggleIcon.classList.remove("bx-hide");
        toggleIcon.classList.add("bx-show");
    }
}


// Function to validate password and confirm password
function validateForm() {
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("register-confirmPassword").value;

    if (password !== confirmPassword) {
        alert("Passwords do not match. Please try again.");
        return false; // Prevent form submission
    }
    return true; // Allow form submission if passwords match
}

// Function to validate reset-password and reset-confirmPassword
function validateForm2() {
    const reset_password = document.getElementById("reset-password").value;
    const reset_confirmPassword = document.getElementById("reset-confirmPassword").value;

    if (reset_password !== reset_confirmPassword) {
        alert("Passwords do not match. Please try again.");
        return false; // Prevent form submission
    }
    return true; // Allow form submission if passwords match
}