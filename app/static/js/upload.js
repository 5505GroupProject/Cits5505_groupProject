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
    
    // Handle text upload form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (uploadStatus) {
                uploadStatus.className = 'alert mt-3';
                uploadStatus.style.display = 'none';
            }
            
            const formData = new FormData(this);
            
            // Disable the submit button to prevent double submission
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Uploading...';
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                console.log('Upload response:', data);
                
                // Show status message
                if (uploadStatus) {
                    uploadStatus.style.display = 'block';
                    
                    if (data.success) {
                        uploadStatus.className = 'alert alert-success mt-3';
                        statusMessage.textContent = data.message;
                        
                        // Clear form if upload successful
                        textArea.value = '';
                        const titleInput = document.getElementById('newsTitle');
                        if (titleInput) titleInput.value = '';
                        wordCount.textContent = '0 words, 0 characters';
                        
                        // Reload history after successful upload
                        loadUploadHistory();
                    } else {
                        uploadStatus.className = 'alert alert-danger mt-3';
                        statusMessage.textContent = data.error || 'Upload failed.';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (uploadStatus) {
                    uploadStatus.className = 'alert alert-danger mt-3';
                    statusMessage.textContent = 'An unexpected error occurred.';
                    uploadStatus.style.display = 'block';
                }
            })
            .finally(() => {
                // Re-enable the button
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
            });
        });
    }
    
    // Handle file upload form submission
    if (fileUploadForm) {
        fileUploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (uploadStatus) {
                uploadStatus.className = 'alert mt-3';
                uploadStatus.style.display = 'none';
            }
            
            const formData = new FormData(this);
            
            // Check if file is selected
            const fileInput = this.querySelector('input[type="file"]');
            if (!fileInput.files || !fileInput.files[0]) {
                if (uploadStatus) {
                    uploadStatus.className = 'alert alert-danger mt-3';
                    statusMessage.textContent = 'Please select a file to upload.';
                    uploadStatus.style.display = 'block';
                }
                return;
            }
            
            console.log('File selected:', fileInput.files[0].name);
            
            // Disable the submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Uploading...';
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                console.log('File upload response:', data);
                
                // Show status message
                if (uploadStatus) {
                    uploadStatus.style.display = 'block';
                    
                    if (data.success) {
                        uploadStatus.className = 'alert alert-success mt-3';
                        statusMessage.textContent = data.message;
                        
                        // Clear file input and title
                        fileInput.value = '';
                        const titleInput = document.getElementById('fileTitle');
                        if (titleInput) titleInput.value = '';
                        
                        // Reload history after successful upload
                        loadUploadHistory();
                    } else {
                        uploadStatus.className = 'alert alert-danger mt-3';
                        statusMessage.textContent = data.error || 'Upload failed.';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (uploadStatus) {
                    uploadStatus.className = 'alert alert-danger mt-3';
                    statusMessage.textContent = 'An unexpected error occurred.';
                    uploadStatus.style.display = 'block';
                }
            })
            .finally(() => {
                // Re-enable the button
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
            });
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
        
        fetch('/api/uploads/history')
            .then(response => {
                console.log('History API response status:', response.status);
                return response.json();
            })
            .then(data => {
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
                                <a href="/view/${upload.id}" class="btn btn-sm btn-primary">View</a>
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
    
    // Load upload history when page loads
    loadUploadHistory();
});