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
    

    // Get form elements
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    
    // Login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Add form validation here instead
            if (!this.checkValidity()) {
                this.classList.add('was-validated');
                return;
            }
            
            const formData = new FormData(this);
            
            // Prevent duplicate submissions
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Signing in...';
            }
            
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
                    
                    // Re-enable the button
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = 'Sign In';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Re-enable the button
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Sign In';
                }
            });
        });
    }
    
    // Register form submission
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Add form validation here instead
            if (!this.checkValidity()) {
                this.classList.add('was-validated');
                return;
            }
            
            const formData = new FormData(this);
            
            // Prevent duplicate submissions
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Creating Account...';
            }
            
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
                    
                    // Re-enable the button
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = 'Create Account';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Show general error message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger';
                alertDiv.innerHTML = 'An error occurred. Please try again.';
                document.getElementById('flashMessages').appendChild(alertDiv);
                
                // Re-enable the button
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Create Account';
                }
            });
        });
    }
    
    // Forgot Password form submission - Fixed to prevent multiple submissions
    if (forgotPasswordForm) {
        // Flag to prevent duplicate submissions
        let isSubmitting = false;
        
        // Create a verification code display element for later use
        const codeDisplayContainer = document.createElement('div');
        codeDisplayContainer.id = 'codeDisplayContainer';
        codeDisplayContainer.className = 'verification-code-display mb-3';
        codeDisplayContainer.style.display = 'none';
        
        // Find where to insert our code display (right after the send code button)
        const sendCodeButton = forgotPasswordForm.querySelector('button[value="send_code"]');
        if (sendCodeButton && sendCodeButton.parentNode) {
            sendCodeButton.parentNode.after(codeDisplayContainer);
        }
        
        // Remove any existing event listeners by cloning the node
        const newForgotPasswordForm = forgotPasswordForm.cloneNode(true);
        if (forgotPasswordForm.parentNode) {
            forgotPasswordForm.parentNode.replaceChild(newForgotPasswordForm, forgotPasswordForm);
        }
        
        // Reference the new form
        const resetForm = document.getElementById('forgotPasswordForm');
        
        if (resetForm) {
            resetForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Check if form is already being submitted
                if (isSubmitting) {
                    console.log('Preventing duplicate submission');
                    return;
                }
                
                // Add form validation here instead
                if (!this.checkValidity()) {
                    this.classList.add('was-validated');
                    return;
                }
                
                // Set flag to prevent duplicate submissions
                isSubmitting = true;
                
                // Get the active button and disable it to prevent multiple clicks
                const activeButton = document.activeElement;
                const originalButtonText = activeButton.innerHTML;
                activeButton.disabled = true;
                activeButton.innerHTML = 'Processing...';
                
                // Get the actual form action URL directly
                const formAction = resetForm.getAttribute('action');
                
                const formData = new FormData(this);
                const activeButtonName = document.activeElement.name;
                const activeButtonValue = document.activeElement.value;
                
                // Get which action we're performing (send_code or verify_code)
                const action = (activeButtonName === 'action') ? activeButtonValue : 'verify_code';
                console.log('Forgot password action:', action);
                
                fetch(formAction, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    // Try to parse as JSON, but if it fails, return the response for further processing
                    return response.json().catch(() => response);
                })
                .then(data => {
                    // Reset submission flag
                    isSubmitting = false;
                    
                    // Re-enable the button
                    activeButton.disabled = false;
                    activeButton.innerHTML = originalButtonText;
                    
                    // If we get a redirect, it means the server wants us to go to the next page
                    if (data.redirect) {
                        window.location.href = data.redirect;
                        return;
                    }
                    
                    // If we have JSON data with success or error
                    if (data.success) {
                        // Clear any existing alerts
                        const flashMessages = document.getElementById('flashMessages');
                        flashMessages.innerHTML = '';
                        
                        // Show success message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success';
                        alertDiv.innerHTML = data.success;                    
                        flashMessages.appendChild(alertDiv);
                        
                        // If we just sent the code, highlight the verification code field
                        if (action === 'send_code') {
                            // Extract the verification code from the success message
                            const codeMatch = data.success.match(/\d{6}/);
                            const verificationCode = codeMatch ? codeMatch[0] : null;
                            
                            if (verificationCode) {
                                // Display the verification code prominently
                                const codeDisplayContainer = document.getElementById('codeDisplayContainer');
                                if (codeDisplayContainer) {
                                    codeDisplayContainer.innerHTML = `
                                        <div class="code-box">
                                            <h5>Your Verification Code:</h5>
                                            <div class="code-value">${verificationCode}</div>
                                            <p class="code-hint">(Enter this code below)</p>
                                        </div>
                                    `;
                                    codeDisplayContainer.style.display = 'block';
                                }
                            }
                            
                            // Show and highlight the verification code field
                            const codeInput = document.getElementById('verificationCode');
                            if (codeInput) {
                                // Make the verification code section visible
                                const verificationSection = document.querySelector('.verification-section');
                                if (verificationSection) {
                                    verificationSection.style.display = 'block';
                                }
                                
                                // Focus on the input
                                codeInput.focus();
                                
                                // Make the verification code section more visible
                                codeInput.parentElement.classList.add('highlight-input');
                                
                                // Optionally scroll to the verification code section
                                codeInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }
                        } else if (action === 'verify_code' && data.redirect) {
                            // If verification successful and we have a redirect URL
                            setTimeout(() => {
                                window.location.href = data.redirect;
                            }, 1500);
                        }
                    } else if (data.error) {
                        // Show error message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-danger';
                        alertDiv.innerHTML = data.error;
                        
                        // Clear any existing alerts
                        const flashMessages = document.getElementById('flashMessages');
                        flashMessages.innerHTML = '';
                        flashMessages.appendChild(alertDiv);
                    }
                })
                .catch(error => {
                    // Reset submission flag
                    isSubmitting = false;
                    
                    // Re-enable the button
                    activeButton.disabled = false;
                    activeButton.innerHTML = originalButtonText;
                    
                    console.error('Error in forgot password form:', error);
                    
                    // Show general error message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger';
                    alertDiv.innerHTML = 'An error occurred. Please try again.';
                    
                    const flashMessages = document.getElementById('flashMessages');
                    flashMessages.innerHTML = '';
                    flashMessages.appendChild(alertDiv);
                });
            });
        }
    }
});