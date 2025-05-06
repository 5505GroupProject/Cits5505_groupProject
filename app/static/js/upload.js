document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const uploadForm = document.getElementById('uploadForm');
    const fileUploadForm = document.getElementById('fileUploadForm');
    const uploadStatus = document.getElementById('uploadStatus');
    const statusMessage = document.getElementById('statusMessage');
    const uploadHistory = document.getElementById('uploadHistory');
    
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
    
    // File upload button functionality
    const fileInput = document.getElementById('file');
    const fileSelectBtn = document.getElementById('fileSelectBtn');
    const selectedFileName = document.getElementById('selectedFileName');
    
    if (fileSelectBtn && fileInput && selectedFileName) {
        fileSelectBtn.addEventListener('click', function() {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFileName.textContent = this.files[0].name;
            } else {
                selectedFileName.textContent = 'No file selected';
            }
        });
    }
    
    // Handle text upload form submission via AJAX (if using API endpoint directly)
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // If we want to handle via normal form submission (which will redirect to test_page after analysis)
            // then we don't need to prevent default
            // e.preventDefault();
            
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
    if (fileUploadForm) {
        fileUploadForm.addEventListener('submit', function(e) {
            // We're handling via normal form submission now for sentiment analysis
            // e.preventDefault();
            
            // Check if file is selected
            const fileInput = this.querySelector('input[type="file"]');
            if (!fileInput.files || !fileInput.files[0]) {
                if (uploadStatus) {
                    uploadStatus.className = 'alert alert-danger mt-3';
                    statusMessage.textContent = 'Please select a file to upload.';
                    uploadStatus.style.display = 'block';
                }
                e.preventDefault(); // Prevent form submission only if no file selected
                return;
            }
            
            console.log('File selected:', fileInput.files[0].name);
            
            // Disable the submit button
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
    
    // Function to load upload history
    function loadUploadHistory() {
        if (!uploadHistory) {
            console.error('Upload history element not found');
            return;
        }
        
        console.log('Loading upload history...');
        uploadHistory.innerHTML = '<p class="text-center text-muted">Loading history...</p>';
        
        fetch('/upload/history')
            .then(response => {
                console.log('History API response status:', response.status);
                
                if (!response.ok) {
                    if (response.status === 401) {
                        uploadHistory.innerHTML = '<p class="text-center text-warning">Please log in to view your upload history.</p>';
                    } else {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return null;
                }
                
                return response.json();
            })
            .then(data => {
                if (!data) return; // Skip processing if no data (from auth error)
                
                console.log('History data:', data);
                
                if (data.success && data.uploads) {
                    if (data.uploads.length === 0) {
                        uploadHistory.innerHTML = '<p class="text-center text-muted">No uploads yet.</p>';
                        return;
                    }
                    
                    uploadHistory.innerHTML = '';
                    
                    // Create a table for better display
                    const table = document.createElement('table');
                    table.className = 'table table-striped';
                    
                    // Add table header
                    const thead = document.createElement('thead');
                    thead.innerHTML = `
                        <tr>
                            <th>Title</th>
                            <th>Date</th>
                            <th>Preview</th>
                            <th>Actions</th>
                        </tr>
                    `;
                    table.appendChild(thead);
                    
                    // Add table body
                    const tbody = document.createElement('tbody');
                    
                    data.uploads.forEach(upload => {
                        const tr = document.createElement('tr');
                        
                        // Make sure values exist, provide fallbacks
                        const title = upload.title || 'Untitled';
                        const date = upload.created_at || 'Unknown date';
                        const preview = upload.preview || 'No preview available';
                        
                        tr.innerHTML = `
                            <td>${title}</td>
                            <td>${date}</td>
                            <td>${preview}</td>
                            <td>
                                <a href="/upload/view/${upload.id}" class="btn btn-sm btn-primary">View</a>
                            </td>
                        `;
                        
                        tbody.appendChild(tr);
                    });
                    
                    table.appendChild(tbody);
                    uploadHistory.appendChild(table);
                    
                } else {
                    console.error('Error in history response:', data);
                    uploadHistory.innerHTML = '<p class="text-center text-danger">Error loading history.</p>';
                }
            })
            .catch(error => {
                console.error('Error loading history:', error);
                uploadHistory.innerHTML = '<p class="text-center text-danger">Failed to load history.</p>';
            });
    }
    
    // Load upload history when page loads, but only if the element exists
    if (document.getElementById('uploadHistory')) {
        loadUploadHistory();
    }
});