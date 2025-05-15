// Ensure Bootstrap components are initialized
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle flash messages auto-dismiss
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            setTimeout(() => bsAlert.close(), 5000);
        });
    }, 100);
});
document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('.site-header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            setTimeout(() => bsAlert.close(), 5000);
        });
    }, 100);
      // Handle Analysis button click
    const navAnalysisBtn = document.querySelector('.nav-analysis');
    if (navAnalysisBtn) {
        navAnalysisBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            try {
                // Show loading state (optional)
                this.classList.add('disabled');
                
                // Fetch the user's latest analysis result
                const response = await fetch('/api/latest_analysis');
                const data = await response.json();
                
                if (data.success && data.url_path) {
                    // Navigate to the latest analysis result
                    window.location.href = `/analysis/${data.url_path}`;
                } else {
                    // If no analysis results exist, redirect to upload page
                    // The flash message will be handled by the server
                    window.location.href = '/upload';
                }
            } catch (error) {
                console.error('Error fetching latest analysis:', error);
                // Fallback to upload page in case of error
                window.location.href = '/upload';
            } finally {
                // Remove loading state
                this.classList.remove('disabled');
            }
        });
    }
});