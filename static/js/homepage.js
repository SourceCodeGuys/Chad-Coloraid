// Toggle navigation menu for responsive design
function myMenuFunction() {
    var navMenu = document.getElementById("navMenu");
    if (navMenu.className === "nav-menu") {
        navMenu.className += " responsive";
    } else {
        navMenu.className = "nav-menu";
    }
}

// Show Login Form
function login() {
    var x = document.getElementById("login");
    var y = document.getElementById("register");
    var z = document.getElementById("forgotPassword");
    var loginBtn = document.getElementById("loginBtn");
    var registerBtn = document.getElementById("registerBtn");

    // Manage form visibility and positioning
    x.style.left = "4px";
    y.style.right = "-520px";
    z.style.right = "-520px";
    x.style.opacity = 1;
    y.style.opacity = 0;
    z.style.opacity = 0;

    // Update button classes
    loginBtn.className = "btn white-btn";
    registerBtn.className = "btn";
}

// Show Registration Form
function register() {
    var x = document.getElementById("login");
    var y = document.getElementById("register");
    var z = document.getElementById("forgotPassword");
    var loginBtn = document.getElementById("loginBtn");
    var registerBtn = document.getElementById("registerBtn");

    // Manage form visibility and positioning
    x.style.left = "-510px";
    y.style.right = "5px";
    z.style.right = "-520px";
    x.style.opacity = 0;
    y.style.opacity = 1;
    z.style.opacity = 0;

    // Update button classes
    loginBtn.className = "btn";
    registerBtn.className = "btn white-btn";
}

// Show Forgot Password Form
function showForgotPassword() {
    var x = document.getElementById("login");
    var y = document.getElementById("register");
    var z = document.getElementById("forgotPassword");

    // Manage form visibility and positioning
    x.style.left = "-510px";
    y.style.right = "-520px";
    z.style.right = "5px";
    x.style.opacity = 0;
    y.style.opacity = 0;
    z.style.opacity = 1;
}
