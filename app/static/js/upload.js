document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const uploadForm = document.getElementById('uploadForm');
    const fileUploadForm = document.getElementById('fileUploadForm');
    const fileInput = document.getElementById('file');
    const selectedFileName = document.getElementById('selectedFileName');
    const analyzeFileBtn = document.getElementById('analyzeFileBtn');
    
    // Initialize word counter
    const textArea = document.getElementById('newsContent');
    const wordCount = document.getElementById('wordCount');
    
    if (textArea && wordCount) {
        textArea.addEventListener('input', function() {
            const text = this.value;
            const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
            const chars = text.length;
            wordCount.textContent = `${words} words, ${chars} characters`;
        });
    }
    
    // Clear button functionality
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn && textArea) {
        clearBtn.addEventListener('click', function() {
            textArea.value = '';
            const titleInput = document.getElementById('newsTitle');
            if (titleInput) titleInput.value = '';
            wordCount.textContent = '0 words, 0 characters';
        });
    }
    
    // File input change handler
    if (fileInput && selectedFileName) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFileName.textContent = this.files[0].name;
            } else {
                selectedFileName.textContent = 'No file selected';
            }
        });
    }
    
    // Handle text upload form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Disable the submit button to prevent double submission
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalBtnText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = 'Uploading & Analyzing...';
                
                // Enable the button after a short delay (form will reload page)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalBtnText;
                }, 1500);
            }
        });
    }
    
    // Handle file upload form submission
    if (fileUploadForm && analyzeFileBtn) {
        fileUploadForm.addEventListener('submit', function(e) {
            // Check if file is selected
            if (!fileInput.files || !fileInput.files[0]) {
                e.preventDefault(); // Prevent form submission
                alert('Please select a file to upload.');
                return false;
            }
            
            console.log('File selected:', fileInput.files[0].name);
            
            // Show submission is in progress
            const originalBtnText = analyzeFileBtn.textContent;
            analyzeFileBtn.disabled = true;
            analyzeFileBtn.textContent = 'Uploading & Analyzing...';
            
            // Enable the button after a short delay (form will reload page)
            setTimeout(function() {
                analyzeFileBtn.disabled = false;
                analyzeFileBtn.textContent = originalBtnText;
            }, 1500);
        });
    }

    // Load upload history via AJAX to ensure fresh data after login
    loadUploadHistory();
});

// Function to load upload history
function loadUploadHistory() {
    // Show loading spinner
    const loadingSpinner = document.getElementById('historyLoadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'block';
    }

    fetch('/upload/history')
        .then(response => response.json())
        .then(data => {
            // Hide loading spinner
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }

            if (data.success && data.uploads) {
                updateUploadHistoryTable(data.uploads);
            } else {
                console.error('Failed to load upload history:', data.error);
            }
        })
        .catch(error => {
            // Hide loading spinner on error too
            if (loadingSpinner) {
                loadingSpinner.style.display = 'none';
            }
            console.error('Error loading upload history:', error);
        });
}

// Function to update the upload history table with data
function updateUploadHistoryTable(uploads) {
    const historyTableBody = document.querySelector('.upload-history table tbody');
    
    if (!historyTableBody) {
        console.error('Upload history table not found!');
        return;
    }
    
    // Clear existing content
    historyTableBody.innerHTML = '';
    
    if (uploads.length === 0) {
        // If no uploads, show a message
        const messageRow = document.createElement('tr');
        messageRow.innerHTML = '<td colspan="4" class="text-center text-muted">No uploads yet.</td>';
        historyTableBody.appendChild(messageRow);
        return;
    }
    
    // Add each upload to the table
    uploads.forEach(upload => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${upload.title || 'Untitled'}</td>
            <td>${upload.created_at}</td>
            <td>${upload.preview}</td>
            <td>
                <a href="/upload/view/${upload.id}" class="btn btn-sm btn-primary">View</a>
            </td>
        `;
        historyTableBody.appendChild(row);
    });
}