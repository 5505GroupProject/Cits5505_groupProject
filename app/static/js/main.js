// Quick login alert handler - needs smooth animation
document.addEventListener('DOMContentLoaded', function() {
    const loginAlert = document.getElementById('loginAlert');
    const closeBtn = document.getElementById('closeLoginAlert');
    
    if (closeBtn && loginAlert) {
        closeBtn.addEventListener('click', function() {
            loginAlert.classList.add('hiding');
            setTimeout(function() {
                loginAlert.style.display = 'none';
            }, 300); // Match the CSS transition - looks janky otherwise
        });
    }
});