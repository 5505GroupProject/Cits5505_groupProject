document.addEventListener('DOMContentLoaded', function() {
    const shareForm = document.getElementById('shareForm');
    
    if (shareForm) {
        // Handle form submission
        shareForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate selections
            const analysisSelect = document.getElementById('analysis_select');
            const userSelect = document.getElementById('user_select');
            
            if (analysisSelect.selectedOptions.length === 0) {
                showAlert('Please select at least one analysis result to share.', 'danger');
                return;
            }
            
            if (userSelect.selectedOptions.length === 0) {
                showAlert('Please select at least one user to share with.', 'danger');
                return;
            }

            // Get form data
            const formData = new FormData(shareForm);
            
            // Convert FormData to JSON
            const data = {
                analysis_ids: Array.from(analysisSelect.selectedOptions).map(opt => opt.value),
                user_ids: Array.from(userSelect.selectedOptions).map(opt => opt.value),
                message: formData.get('message'),
                permission: formData.get('permission'),
                csrf_token: formData.get('csrf_token')
            };

            // Send share request
            fetch(shareForm.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrf_token')
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(text) });
                }
                return response.text();
            })
            .then(result => {
                showAlert(result, 'success');
                shareForm.reset();
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            })
            .catch(error => {
                showAlert(error.message, 'danger');
            });
        });

        // Add event listeners for select boxes to show selected count
        const analysisSelect = document.getElementById('analysis_select');
        const userSelect = document.getElementById('user_select');
        
        [analysisSelect, userSelect].forEach(select => {
            if (select) {
                select.addEventListener('change', function() {
                    const count = this.selectedOptions.length;
                    const label = this.previousElementSibling;
                    const originalText = label.getAttribute('data-original-text') || label.textContent;
                    
                    if (!label.getAttribute('data-original-text')) {
                        label.setAttribute('data-original-text', originalText);
                    }
                    
                    label.textContent = `${originalText} (${count} selected)`;
                });
            }
        });
    }
});

// Helper function to show alerts
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const form = document.getElementById('shareForm');
    form.insertBefore(alertDiv, form.firstChild);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}