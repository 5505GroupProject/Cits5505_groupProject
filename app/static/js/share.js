document.addEventListener('DOMContentLoaded', function() {
    const shareForm = document.getElementById('shareForm');
    const searchUserBtn = document.getElementById('searchUserBtn');
    const usernameSearch = document.getElementById('usernameSearch');
    const searchResults = document.getElementById('searchResults');
    const userSearchResults = document.getElementById('userSearchResults');
    const connectedUsersList = document.getElementById('connectedUsersList');
    const noConnectionsMsg = document.getElementById('noConnectionsMsg');
    
    // Function to show alert messages
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert alert before the form or any other element
        const container = document.querySelector('.card-body');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 150);
            }, 5000);
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
        
        // Add event listener for the remove button
        removeBtn.addEventListener('click', function() {
            removeUserConnection(user.id);
        });
        
        return li;
    }
    
    // Function to search for users
    function searchUsers(username) {
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
            
            if (data.users && data.users.length > 0) {
                // Show results
                data.users.forEach(user => {
                    const li = createSearchResultItem(user);
                    userSearchResults.appendChild(li);
                });
                searchResults.style.display = 'block';
            } else {
                // No results found
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = 'No users found';
                userSearchResults.appendChild(li);
                searchResults.style.display = 'block';
            }
        })
        .catch(error => {
            showAlert(error.message, 'danger');
        });
    }
    
    // Function to add a user connection
    function addUserConnection(userId) {
        fetch('/share/add-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
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
            
            // Remove from search results
            const searchItem = userSearchResults.querySelector(`li[data-user-id="${userId}"]`);
            if (searchItem) searchItem.remove();
            
            // Add to connected users list
            if (noConnectionsMsg && connectedUsersList) {
                // If there's no connections message, hide it and create the list
                if (noConnectionsMsg.style.display !== 'none') {
                    noConnectionsMsg.style.display = 'none';
                    
                    if (!connectedUsersList) {
                        const ul = document.createElement('ul');
                        ul.id = 'connectedUsersList';
                        ul.className = 'list-group';
                        document.querySelector('.connected-users').appendChild(ul);
                        connectedUsersList = ul;
                    }
                }
            }
            
            // Add to the connected users list
            if (connectedUsersList) {
                const li = createConnectedUserItem(data.user);
                connectedUsersList.appendChild(li);
                
                // Also add to the user_select dropdown
                const userSelect = document.getElementById('user_select');
                if (userSelect) {
                    const option = document.createElement('option');
                    option.value = data.user.id;
                    option.textContent = data.user.username;
                    userSelect.appendChild(option);
                }
            }
            
            // If no more search results, hide the section
            if (userSearchResults.children.length === 0) {
                searchResults.style.display = 'none';
            }
        })
        .catch(error => {
            showAlert(error.message, 'danger');
        });
    }
    
    // Function to remove a user connection
    function removeUserConnection(userId) {
        fetch(`/share/remove-user/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
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
            
            // Remove from connected users list
            const connectedItem = connectedUsersList.querySelector(`li[data-user-id="${userId}"]`);
            if (connectedItem) connectedItem.remove();
            
            // If no more connected users, show the no connections message
            if (connectedUsersList && connectedUsersList.children.length === 0) {
                if (noConnectionsMsg) {
                    noConnectionsMsg.style.display = 'block';
                }
            }
            
            // Also remove from the user_select dropdown
            const userSelect = document.getElementById('user_select');
            if (userSelect) {
                const option = userSelect.querySelector(`option[value="${userId}"]`);
                if (option) option.remove();
            }
        })
        .catch(error => {
            showAlert(error.message, 'danger');
        });
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
    
    // Set up event listeners for remove buttons
    if (connectedUsersList) {
        document.querySelectorAll('.remove-user').forEach(button => {
            button.addEventListener('click', function() {
                const userId = this.parentElement.dataset.userId;
                removeUserConnection(userId);
            });
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
                    const originalLabel = label.textContent.split(' (')[0];
                    label.textContent = count > 0 ? `${originalLabel} (${count} selected)` : originalLabel;
                });
            }
        });
    }
});