document.addEventListener('DOMContentLoaded', function() {
    const shareForm = document.getElementById('shareForm');
    const searchUserBtn = document.getElementById('searchUserBtn');
    const usernameSearch = document.getElementById('usernameSearch');
    const searchResults = document.getElementById('searchResults');
    const userSearchResults = document.getElementById('userSearchResults');
    const connectedUsersList = document.getElementById('connectedUsersList');
    const noConnectionsMsg = document.getElementById('noConnectionsMsg');
    
    // Setup user connection selector dropdown with any existing connections
    function setupUserSelectDropdown() {
        const userSelect = document.getElementById('user_select');
        if (!userSelect || !connectedUsersList) return;
        
        // Clear the dropdown first
        userSelect.innerHTML = '';
        
        // Get all users from the connectedUsersList and add them to the dropdown
        const userItems = connectedUsersList.querySelectorAll('li[data-user-id]');
        userItems.forEach(item => {
            const userId = item.dataset.userId;
            const username = item.querySelector('span').textContent;
            
            const option = document.createElement('option');
            option.value = userId;
            option.textContent = username;
            userSelect.appendChild(option);
        });
    }
    
    // Add user connection function - direct DOM manipulation with animations
    function addUserConnection(userId) {
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';
        
        fetch('/share/add-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => { throw new Error(data.error || 'Error adding user') });
            }
            return response.json();
        })
        .then(data => {
            showAlert(data.message, 'success');
            
            // Remove from search results with animation
            const searchItem = userSearchResults.querySelector(`li[data-user-id="${userId}"]`);
            if (searchItem) {
                searchItem.classList.add('fade-out');
                setTimeout(() => {
                    searchItem.remove();
                    
                    // If no more search results, hide the section with animation
                    if (userSearchResults.children.length === 0) {
                        searchResults.style.opacity = '0';
                        setTimeout(() => {
                            searchResults.style.display = 'none';
                            searchResults.style.opacity = '1';
                        }, 300);
                    }
                }, 500);
            }
            
            // Add to connected users list with animation
            if (connectedUsersList) {
                // Hide no connections message if it exists
                if (noConnectionsMsg) {
                    noConnectionsMsg.style.display = 'none';
                }
                
                // Create and add the new user item
                const li = createConnectedUserItem(data.user);
                li.style.opacity = '0';
                connectedUsersList.appendChild(li);
                
                // Trigger reflow for animation
                void li.offsetWidth;
                
                // Apply fade-in animation
                li.classList.add('fade-in');
                
                // Also add to the user_select dropdown
                setupUserSelectDropdown();
            }
        })
        .catch(error => {
            showAlert(error.message, 'danger');
        });
    }
    
    // Remove user connection function - direct DOM manipulation with animation
    function removeUserConnection(userId) {
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';
        
        fetch(`/share/remove-user/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => { throw new Error(data.error || 'Error removing user') });
            }
            return response.json();
        })
        .then(data => {
            showAlert(data.message, 'success');
            
            // Remove from connected users list with animation
            const connectedItem = connectedUsersList.querySelector(`li[data-user-id="${userId}"]`);
            if (connectedItem) {
                // Add fade-out animation class
                connectedItem.classList.add('fade-out');
                
                // Remove element after animation completes
                setTimeout(() => {
                    connectedItem.remove();
                    
                    // If no more connected users, show the no connections message with animation
                    if (connectedUsersList && connectedUsersList.children.length === 0) {
                        if (noConnectionsMsg) {
                            noConnectionsMsg.style.display = 'block';
                            noConnectionsMsg.classList.add('fade-in');
                        }
                    }
                    
                    // Update dropdown
                    setupUserSelectDropdown();
                }, 500); // Match this timing with the CSS animation duration
            }
        })
        .catch(error => {
            showAlert(error.message, 'danger');
        });
    }
    
    // Initialize dropdown on page load
    setupUserSelectDropdown();
    
    // Setup event delegation for remove buttons
    if (connectedUsersList) {
        connectedUsersList.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-user')) {
                const userId = e.target.closest('li').dataset.userId;
                if (userId) {
                    removeUserConnection(userId);
                }
            }
        });
    }
    
    // Function to show alert messages with enhanced animation
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade`;
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi ${getAlertIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert alert before the form or any other element
        const container = document.querySelector('.card-body');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Trigger reflow for animation
            void alertDiv.offsetWidth;
            
            // Show the alert with animation
            alertDiv.classList.add('show');
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 300);
            }, 5000);
        }
    }
    
    // Helper function to get appropriate icon for alert type
    function getAlertIcon(type) {
        switch(type) {
            case 'success':
                return 'bi-check-circle-fill';
            case 'danger':
                return 'bi-exclamation-triangle-fill';
            case 'warning':
                return 'bi-exclamation-circle-fill';
            case 'info':
                return 'bi-info-circle-fill';
            default:
                return 'bi-bell-fill';
        }
    }
    
    // Function to create a search result item
    function createSearchResultItem(user) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.dataset.userId = user.id;
        
        const span = document.createElement('span');
        span.textContent = user.username;
        
        const addBtn = document.createElement('button');
        addBtn.className = 'btn btn-sm btn-success add-user';
        addBtn.textContent = 'Add';
        
        li.appendChild(span);
        li.appendChild(addBtn);
        
        // Add event listener for the add button
        addBtn.addEventListener('click', function() {
            addUserConnection(user.id);
        });
        
        return li;
    }
    
    // Function to create a connected user item
    function createConnectedUserItem(user) {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.dataset.userId = user.id;
        
        const span = document.createElement('span');
        span.textContent = user.username;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-danger remove-user';
        removeBtn.textContent = 'Remove';
        
        li.appendChild(span);
        li.appendChild(removeBtn);
        
        return li;
    }
    
    // Function to search for users with enhanced animations
    function searchUsers(username) {
        // Show loading state
        const searchBtn = document.getElementById('searchUserBtn');
        const originalBtnText = searchBtn.innerHTML;
        searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...';
        searchBtn.disabled = true;
        
        // If search results are already visible, fade them out first
        if (searchResults.style.display === 'block') {
            searchResults.style.opacity = '0';
            setTimeout(() => {
                performSearch();
            }, 300);
        } else {
            performSearch();
        }
        
        function performSearch() {
            fetch('/share/search-user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                },
                body: JSON.stringify({ username })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => { throw new Error(data.error || 'Error searching for users') });
                }
                return response.json();
            })
            .then(data => {
                // Clear previous results
                userSearchResults.innerHTML = '';
                
                // Hide search results initially for animation
                searchResults.style.opacity = '0';
                searchResults.style.display = 'block';
                
                if (data.users && data.users.length > 0) {
                    // Create results with slight delay between each for staggered animation
                    data.users.forEach((user, index) => {
                        setTimeout(() => {
                            const li = createSearchResultItem(user);
                            li.style.opacity = '0';
                            userSearchResults.appendChild(li);
                            
                            // Trigger reflow for animation
                            void li.offsetWidth;
                            
                            // Apply fade-in animation
                            li.style.opacity = '1';
                            li.style.transition = 'opacity 0.3s ease';
                        }, index * 100);
                    });
                } else {
                    // No results found
                    const li = document.createElement('li');
                    li.className = 'list-group-item text-center';
                    li.innerHTML = '<i class="bi bi-search me-2"></i>No users found matching "' + username + '"';
                    userSearchResults.appendChild(li);
                }
                
                // Fade in the search results container
                setTimeout(() => {
                    searchResults.style.opacity = '1';
                    searchResults.style.transition = 'opacity 0.3s ease';
                }, 100);
                
                // Restore button state
                searchBtn.innerHTML = originalBtnText;
                searchBtn.disabled = false;
            })
            .catch(error => {
                showAlert(error.message, 'danger');
                
                // Restore button state
                searchBtn.innerHTML = originalBtnText;
                searchBtn.disabled = false;
            });
        }
    }
    
    // Set up event listeners for search
    if (searchUserBtn) {
        searchUserBtn.addEventListener('click', function() {
            const username = usernameSearch.value.trim();
            if (username) {
                searchUsers(username);
            } else {
                showAlert('Please enter a username to search', 'warning');
            }
        });
    }
    
    if (usernameSearch) {
        usernameSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const username = usernameSearch.value.trim();
                if (username) {
                    searchUsers(username);
                } else {
                    showAlert('Please enter a username to search', 'warning');
                }
            }
        });
    }
    
    // Original share form handling
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

            // Show loading state on submit button
            const submitBtn = shareForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sharing...';
            submitBtn.disabled = true;
            
            // Add overlay to form
            const overlay = document.createElement('div');
            overlay.style.position = 'absolute';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(255,255,255,0.6)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '100';
            overlay.style.borderRadius = '15px';
            overlay.style.opacity = '0';
            overlay.style.transition = 'opacity 0.3s ease';
            
            const formCard = shareForm.closest('.card-body');
            if (formCard) {
                formCard.style.position = 'relative';
                formCard.appendChild(overlay);
                setTimeout(() => { overlay.style.opacity = '1'; }, 0);
            }
            
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
                
                // Show success animation
                overlay.innerHTML = '<div class="text-center"><i class="bi bi-check-circle-fill text-success" style="font-size: 3rem;"></i><h4 class="mt-3">Shared Successfully!</h4><p>Redirecting...</p></div>';
                
                // Reset form with visual feedback
                shareForm.reset();
                
                // Reset select labels if they had (x selected) text
                const labels = shareForm.querySelectorAll('label[for="analysis_select"], label[for="user_select"]');
                labels.forEach(label => {
                    const originalLabel = label.textContent.split(' (')[0];
                    label.textContent = originalLabel;
                });
                
                // Redirect after a delay
                setTimeout(() => {
                    window.location.reload();
                }, 1800);
            })
            .catch(error => {
                // Remove overlay
                if (overlay) {
                    overlay.style.opacity = '0';
                    setTimeout(() => { overlay.remove(); }, 300);
                }
                
                // Restore button
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                // Show error
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
                    const originalLabel = label.textContent.split(' (')[0];
                    label.textContent = count > 0 ? `${originalLabel} (${count} selected)` : originalLabel;
                });
            }
        });
    }
});