document.addEventListener('DOMContentLoaded', function() {
    // Grab all our form elements - why does querySelector feel so clunky sometimes?
    const uploadForm = document.getElementById('uploadForm');
    const fileUploadForm = document.getElementById('fileUploadForm');
    const fileInput = document.getElementById('file');
    const selectedFileName = document.getElementById('selectedFileName');
    const analyzeFileBtn = document.getElementById('analyzeFileBtn');
    
    // Word counter setup - everyone loves stats
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
    
    // Clear button - because starting over shouldn't require page refresh
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn && textArea) {
        clearBtn.addEventListener('click', function() {
            textArea.value = '';
            const titleInput = document.getElementById('newsTitle');
            if (titleInput) titleInput.value = '';
            wordCount.textContent = '0 words, 0 characters';
        });
    }
    
    // Show the file name when selected - UX 101
    if (fileInput && selectedFileName) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFileName.textContent = this.files[0].name;
            } else {
                selectedFileName.textContent = 'No file selected';
            }
        });
    }
    
    // Handle text upload form - with that nice "processing" button state
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Disable the submit button to prevent double submission
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalBtnText = submitBtn.textContent;
                submitBtn.disabled = true;
                submitBtn.textContent = 'Uploading & Analyzing...';
                
                // Re-enable after a delay - should be plenty of time for form submission
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalBtnText;
                }, 1500);
            }
        });
    }
    
    // File upload validation - catch empty uploads before server has to
    if (fileUploadForm && analyzeFileBtn) {
        fileUploadForm.addEventListener('submit', function(e) {
            // Check if file is selected
            if (!fileInput.files || !fileInput.files[0]) {
                e.preventDefault(); // Prevent form submission
                alert('Please select a file to upload.');
                return false;
            }
            
            console.log('File selected:', fileInput.files[0].name);
            
            // Show that something's happening - users hate waiting with no feedback
            const originalBtnText = analyzeFileBtn.textContent;
            analyzeFileBtn.disabled = true;
            analyzeFileBtn.textContent = 'Uploading & Analyzing...';
            
            // Re-enable after a delay
            setTimeout(function() {
                analyzeFileBtn.disabled = false;
                analyzeFileBtn.textContent = originalBtnText;
            }, 1500);
        });
    }

    // News Search Tab - maybe replace with a better API later?
    const searchTab = document.getElementById('search-tab');
    const latestNewsFeed = document.getElementById('latestNewsFeed');
    const categoryButtons = document.querySelectorAll('.news-category-btn');
    let currentCategory = 'general';
    
    // Handle category switching - could make this more elegant later
    if (categoryButtons.length > 0) {
        categoryButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Update active state
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Get the selected category and load news
                currentCategory = this.getAttribute('data-category');
                loadLatestNews(currentCategory);
            });
        });
    }
    
    // Load news only when tab is clicked - save those API calls!
    if (searchTab) {
        searchTab.addEventListener('click', function() {
            // Only load latest news if we haven't already
            if (latestNewsFeed && latestNewsFeed.children.length <= 1) {
                loadLatestNews(currentCategory);
            }
        });
    }

    // News Search Functionality - lots of elements to keep track of
    const searchNewsBtn = document.getElementById('searchNewsBtn');
    const newsSearchQuery = document.getElementById('newsSearchQuery');
    const newsResultsList = document.getElementById('newsResultsList');
    const newsSearchSpinner = document.getElementById('newsSearchSpinner');
    const selectedArticlePreview = document.getElementById('selectedArticlePreview');
    const previewArticleTitle = document.getElementById('previewArticleTitle');
    const previewArticleContent = document.getElementById('previewArticleContent');
    const closePreviewBtn = document.getElementById('closePreviewBtn');
    const articleUploadForm = document.getElementById('articleUploadForm');
    const uploadArticleTitle = document.getElementById('uploadArticleTitle');
    const uploadArticleContent = document.getElementById('uploadArticleContent');
    const searchResultsPlaceholder = document.querySelector('.search-results-placeholder');

    // Handle news search
    if (searchNewsBtn && newsSearchQuery) {
        // Allow pressing Enter in the search box
        newsSearchQuery.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchNewsBtn.click();
            }
        });

        searchNewsBtn.addEventListener('click', function() {
            const query = newsSearchQuery.value.trim();
            if (!query) {
                alert('Please enter a search query');
                return;
            }

            // Show spinner, hide placeholder
            if (newsSearchSpinner) newsSearchSpinner.classList.remove('d-none');
            if (searchResultsPlaceholder) searchResultsPlaceholder.classList.add('d-none');
            if (newsResultsList) newsResultsList.innerHTML = '';
            
            // Hide article preview if it's showing
            if (selectedArticlePreview) selectedArticlePreview.classList.add('d-none');

            // Make API request to search for news
            fetch(`/upload/search-news?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    // Hide spinner
                    if (newsSearchSpinner) newsSearchSpinner.classList.add('d-none');
                    
                    if (data.success && data.articles && data.articles.length > 0) {
                        displaySearchResults(data.articles);
                    } else {
                        // Show error or no results message
                        if (newsResultsList) {
                            if (data.error && data.error.includes('API key')) {
                                // API key error
                                newsResultsList.innerHTML = `
                                    <div class="alert alert-warning">
                                        <strong>API Key Missing:</strong> ${data.error}
                                        <p class="mt-2"><small>To use this feature, you need to get an API key from <a href="https://newsapi.org/" target="_blank">NewsAPI.org</a> and add it to your config.py file.</small></p>
                                    </div>
                                `;
                            } else {
                                // No results found
                                newsResultsList.innerHTML = `
                                    <div class="alert alert-info">
                                        No articles found for "${query}". Please try a different search term.
                                    </div>
                                `;
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Error searching for news:', error);
                    // Hide spinner
                    if (newsSearchSpinner) newsSearchSpinner.classList.add('d-none');
                    
                    // Show error message
                    if (newsResultsList) {
                        newsResultsList.innerHTML = `
                            <div class="alert alert-danger">
                                An error occurred while searching for news. Please try again.
                            </div>
                        `;
                    }
                });
        });
    }
    
    // Function to load latest news headlines - API requests are fun
    function loadLatestNews(category = 'general') {
        const latestNewsSpinner = document.getElementById('latestNewsSpinner');
        if (latestNewsSpinner) latestNewsSpinner.style.display = 'block';
        
        // Fetch from our Flask backend - keeping API key safe server-side
        fetch(`/upload/latest-news?category=${encodeURIComponent(category)}`)
            .then(response => response.json())
            .then(data => {
                // Hide spinner
                if (latestNewsSpinner) latestNewsSpinner.style.display = 'none';
                
                if (data.success && data.articles && data.articles.length > 0) {
                    displayLatestNews(data.articles);
                } else {
                    // Show error message - be helpful about API key issues
                    if (latestNewsFeed) {
                        latestNewsFeed.innerHTML = `
                            <div class="col-12">
                                <div class="alert alert-warning">
                                    <strong>Note:</strong> ${data.error || 'No headlines available at the moment. Please try again later.'}
                                    ${data.error && data.error.includes('API key') ? 
                                    '<p class="mt-2"><small>To use this feature, you need to get an API key from <a href="https://newsapi.org/" target="_blank">NewsAPI.org</a> and add it to your config.py file.</small></p>' : ''}
                                </div>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Error loading latest news:', error);
                // Hide spinner
                if (latestNewsSpinner) latestNewsSpinner.style.display = 'none';
                
                // Show error message - keep it friendly
                if (latestNewsFeed) {
                    latestNewsFeed.innerHTML = `
                        <div class="col-12">
                            <div class="alert alert-danger">
                                An error occurred while loading latest news. Please try again later.
                            </div>
                        </div>
                    `;
                }
            });
    }
    
    // Making pretty news cards - Bootstrap makes this easier
    function displayLatestNews(articles) {
        if (!latestNewsFeed) return;
        
        latestNewsFeed.innerHTML = ''; // Clear any existing content
        
        // Limit to only 3 latest headlines
        const limitedArticles = articles.slice(0, 3);
        
        limitedArticles.forEach(article => {
            // Get image or placeholder
            const imageUrl = article.urlToImage || 'https://placehold.co/600x400?text=No+Image';
            
            // Create a news card without date
            const newsCard = document.createElement('div');
            newsCard.className = 'col-md-4 mb-4';
            newsCard.innerHTML = `
                <div class="card h-100">
                    <img src="${imageUrl}" class="card-img-top" alt="${article.title}" onerror="this.src='https://placehold.co/600x400?text=No+Image'">
                    <div class="card-body">
                        <h5 class="card-title">${article.title}</h5>
                        <p class="card-text small text-muted">${article.source}</p>
                        <p class="card-text">${article.description || 'No description available'}</p>
                    </div>
                    <div class="card-footer bg-transparent">
                        <button class="btn btn-outline-primary btn-sm analyze-article-btn">Select & Analyze</button>
                    </div>
                </div>
            `;
            
            // Add click handler to analyze this article
            const analyzeBtn = newsCard.querySelector('.analyze-article-btn');
            if (analyzeBtn) {
                analyzeBtn.addEventListener('click', function() {
                    selectArticle(article);
                });
            }
            
            latestNewsFeed.appendChild(newsCard);
        });
    }

    // Function to display search results
    function displaySearchResults(articles) {
        if (!newsResultsList) return;

        newsResultsList.innerHTML = ''; // Clear previous results
        
        articles.forEach(article => {
            // Create a result item without date
            const resultItem = document.createElement('button');
            resultItem.className = 'list-group-item list-group-item-action';
            resultItem.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">${article.title}</h5>
                </div>
                <p class="mb-1">${article.description || 'No description available'}</p>
                <small class="text-muted">Source: ${article.source}</small>
            `;
            
            // Add click handler to select this article
            resultItem.addEventListener('click', function() {
                selectArticle(article);
            });
              newsResultsList.appendChild(resultItem);
        });
    }
    
    // Function to select and preview an article
    function selectArticle(article) {
        if (!selectedArticlePreview || !previewArticleTitle || !previewArticleContent) return;
        
        // Check if the article has insufficient content flag
        if (article.contentInsufficient === true) {
            // Show confirmation dialog with a button to visit source URL
            if (confirm(`Article "${article.title}" has insufficient content. The article may be behind a paywall or not accessible.\n\nWould you like to visit the original source website?`)) {
                window.open(article.url, '_blank');
            }
            return; // Stop processing this article
        }
          
        // Extract content from the article - ensure we get full content
        let articleContent = article.content || 'No content available';
        
        // Remove the "[+XXXX chars]" that NewsAPI adds if present
        articleContent = articleContent.replace(/\[\+\d+ chars\]$/, '');
        
        // Remove excessive empty lines (replace 3 or more newlines with just 2)
        articleContent = articleContent.replace(/\n{3,}/g, '\n\n');
        
        // Trim any leading or trailing whitespace
        articleContent = articleContent.trim();
        
        // Debug log to check content length
        console.log("Article content length:", articleContent.length, "chars, Article title:", article.title);
        
        // Show the article preview with full content
        previewArticleTitle.textContent = article.title;
        previewArticleContent.textContent = articleContent;
        selectedArticlePreview.classList.remove('d-none');
        
        // Set the values for the upload form with full content
        if (uploadArticleTitle) uploadArticleTitle.value = article.title;
        if (uploadArticleContent) uploadArticleContent.value = articleContent;
        
        // Update word count if we have a word count element
        if (wordCount) {
            const words = articleContent.trim() === '' ? 0 : articleContent.trim().split(/\s+/).length;
            const chars = articleContent.length;
            wordCount.textContent = `${words} words, ${chars} characters`;
        }
        
        // Update the textArea if it exists (to sync with the news content)
        if (textArea) {
            textArea.value = articleContent;
            // Trigger the input event to update word count if needed
            const inputEvent = new Event('input', { bubbles: true });
            textArea.dispatchEvent(inputEvent);
        }
        
        // Scroll to preview section
        selectedArticlePreview.scrollIntoView({ behavior: 'smooth' });
    }

    // Close preview button handler
    if (closePreviewBtn) {
        closePreviewBtn.addEventListener('click', function() {
            if (selectedArticlePreview) selectedArticlePreview.classList.add('d-none');
        });
    }

    // Handle article upload form submission
    if (articleUploadForm) {
        articleUploadForm.addEventListener('submit', function(e) {
            // We don't prevent default here since we want the form to submit normally to the action URL
            
            // Get the content values for validation
            const title = uploadArticleTitle.value;
            const content = uploadArticleContent.value;
            
            if (!content) {
                e.preventDefault(); // Prevent form submission if no content
                alert('No article content to upload!');
                return false;
            }
            
            // Disable submit button to prevent double-submission
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Uploading & Analyzing...';
                
                // The form will naturally submit and redirect to the visualization page
                // This timeout is just to ensure the button stays disabled during submission
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Upload & Analyze';
                }, 3000);
            }
            
            // Let the form submit naturally to the action URL
            return true;
        });
    }

    // Load history on page load - keeps things fresh after login/logout
    loadUploadHistory();
});

// Function to load upload history
function loadUploadHistory() {
    // Show loading spinner - so it doesn't look broken
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

// Refreshing the history table - keeping DOM manipulation organized
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
    }    // Add each upload to the table
    uploads.forEach(upload => {
        const row = document.createElement('tr');
        row.dataset.uploadId = upload.id; // Store upload ID in the row for easy reference
        
        // Use the analysis URL path if available, otherwise use the regular view upload route
        const analyzeUrl = upload.analysis_url_path 
            ? `/analysis/${upload.analysis_url_path}` 
            : `/upload/view/${upload.id}`;
            
        row.innerHTML = `
            <td>${upload.title || 'Untitled'}</td>
            <td>${upload.created_at}</td>
            <td>${upload.preview}</td>
            <td>
                <a href="${analyzeUrl}" class="btn btn-sm btn-primary">Analyze</a>
                <button type="button" class="btn btn-sm btn-danger delete-upload-btn" data-upload-id="${upload.id}">Delete</button>
            </td>
        `;
        historyTableBody.appendChild(row);
    });
    
    // Adding those delete button listeners - event delegation would be cleaner but this works
    addDeleteButtonListeners();
}

// Adding those delete button listeners - event delegation would be cleaner but this works
function addDeleteButtonListeners() {
    const deleteButtons = document.querySelectorAll('.delete-upload-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const uploadId = this.getAttribute('data-upload-id');
            confirmDeleteUpload(uploadId);
        });
    });
}

// Confirmation before delete - never delete without asking!
function confirmDeleteUpload(uploadId) {
    if (confirm('Are you sure you want to delete this upload? This action cannot be undone.')) {
        deleteUpload(uploadId);
    }
}

// Actually delete the upload - AJAX makes this smooth
function deleteUpload(uploadId) {
    // Get the CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`/upload/delete/${uploadId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Find and remove the row from the table
            const rowToRemove = document.querySelector(`tr[data-upload-id="${uploadId}"]`);
            if (rowToRemove) {
                rowToRemove.remove();
                
                // If no more uploads, show "No uploads yet" message
                const historyTableBody = document.querySelector('.upload-history table tbody');
                if (historyTableBody && historyTableBody.children.length === 0) {
                    const messageRow = document.createElement('tr');
                    messageRow.innerHTML = '<td colspan="4" class="text-center text-muted">No uploads yet.</td>';
                    historyTableBody.appendChild(messageRow);
                }
            }
        } else {
            // Show error message
            alert('Error deleting upload: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error deleting upload:', error);
        alert('An error occurred while deleting the upload. Please try again.');
    });
}