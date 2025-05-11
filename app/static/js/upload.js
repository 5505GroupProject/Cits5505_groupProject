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

    // We're relying on server-rendered history now. The AJAX-based history loading has been removed.
    // The server will provide the full history with the initial page load.
});