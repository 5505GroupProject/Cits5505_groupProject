document.addEventListener('DOMContentLoaded', function() {
    // Form containers
    const loginContainer = document.getElementById('loginContainer');
    const registerContainer = document.getElementById('registerContainer');
    const forgotPasswordContainer = document.getElementById('forgotPasswordContainer');
    
    // Form switching handlers
    document.getElementById('showRegisterForm')?.addEventListener('click', function(e) {
        e.preventDefault();
        loginContainer.style.display = 'none';
        registerContainer.style.display = 'block';
        forgotPasswordContainer.style.display = 'none';
    });
    
    document.getElementById('showLoginForm')?.addEventListener('click', function(e) {
        e.preventDefault();
        loginContainer.style.display = 'block';
        registerContainer.style.display = 'none';
        forgotPasswordContainer.style.display = 'none';
    });
    
    document.getElementById('showForgotPasswordForm')?.addEventListener('click', function(e) {
        e.preventDefault();
        loginContainer.style.display = 'none';
        registerContainer.style.display = 'none';
        forgotPasswordContainer.style.display = 'block';
    });
    
    document.getElementById('backToLoginForm')?.addEventListener('click', function(e) {
        e.preventDefault();
        loginContainer.style.display = 'block';
        registerContainer.style.display = 'none';
        forgotPasswordContainer.style.display = 'none';
    });
    
    // Password confirmation validation
    const passwordField = document.getElementById('reg_password');
    const confirmPasswordField = document.getElementById('confirm-password');
    
    if (passwordField && confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            if (this.value !== passwordField.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Get form elements
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    
    // Login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            // Debug CSRF token
            console.log('CSRF token in login form:', formData.get('csrf_token'));
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin' // Important for CSRF
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success';
                    alertDiv.innerHTML = data.success;
                    document.getElementById('flashMessages').appendChild(alertDiv);
                    
                    // Redirect after a short delay
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1500);
                } else if (data.error) {
                    // Show error message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger';
                    alertDiv.innerHTML = data.error;
                    document.getElementById('flashMessages').appendChild(alertDiv);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
    
    // Register form submission
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            // Debug CSRF token
            console.log('CSRF token in register form:', formData.get('csrf_token'));
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin' // Important for CSRF
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success';
                    alertDiv.innerHTML = data.success;
                    document.getElementById('flashMessages').appendChild(alertDiv);
                    
                    // Redirect after a short delay
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1500);
                } else if (data.error) {
                    // Show error message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger';
                    alertDiv.innerHTML = data.error;
                    document.getElementById('flashMessages').appendChild(alertDiv);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Show general error message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger';
                alertDiv.innerHTML = 'An error occurred. Please try again.';
                document.getElementById('flashMessages').appendChild(alertDiv);
            });
        });
    }
    
    // Similar handler for forgotPasswordForm
    // ...
});