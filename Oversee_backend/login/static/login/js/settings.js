
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Profile Form Submission
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const firstName = document.getElementById('first-name').value;
            const lastName = document.getElementById('last-name').value;
            const email = document.getElementById('email').value;
            
            // Validate form
            if (!email) {
                showAlert('Email is required', 'danger');
                return;
            }
            
            // Send data to server
            fetch('/api/update-profile/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    email: email
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                } else {
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Failed to update profile. Please try again.', 'danger');
            });
        });
    }
    
    // Password Form Submission
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('change-new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            // Validate passwords match
            if (!currentPassword || !newPassword || !confirmPassword) {
                showAlert('All password fields are required', 'danger');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                showAlert('New passwords do not match!', 'danger');
                return;
            }
            
            // Send data to server
            fetch('/api/change-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                    passwordForm.reset();
                } else {
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Failed to change password. Please try again.', 'danger');
            });
        });
    }
    
    // Notification Form Submission
    const notificationForm = document.getElementById('notification-form');
    if (notificationForm) {
        notificationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const browserNotifications = document.getElementById('browser-notifications').checked;
            const emailNotifications = document.getElementById('email-notifications').checked;
            const notificationFrequency = document.querySelector('input[name="notification-frequency"]:checked').id;
            
            // Save to localStorage for client-side persistence
            localStorage.setItem('browser_notifications', browserNotifications);
            localStorage.setItem('email_notifications', emailNotifications);
            localStorage.setItem('notification_frequency', notificationFrequency);
            
            // Send data to server
            fetch('/api/user-preferences/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    type: 'notification',
                    browser_notifications: browserNotifications,
                    email_notifications: emailNotifications,
                    notification_frequency: notificationFrequency.replace('notify-', '')
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                } else {
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Notification settings saved locally. Server sync failed.', 'warning');
            });
        });
        
        // Load saved notification settings from localStorage
        const savedBrowserNotifications = localStorage.getItem('browser_notifications');
        const savedEmailNotifications = localStorage.getItem('email_notifications');
        const savedNotificationFrequency = localStorage.getItem('notification_frequency');
        
        if (savedBrowserNotifications !== null) {
            document.getElementById('browser-notifications').checked = savedBrowserNotifications === 'true';
        }
        
        if (savedEmailNotifications !== null) {
            document.getElementById('email-notifications').checked = savedEmailNotifications === 'true';
        }
        
        if (savedNotificationFrequency) {
            const frequencyElement = document.getElementById(savedNotificationFrequency);
            if (frequencyElement) {
                frequencyElement.checked = true;
            }
        }
    }
    
    // Appearance Form Submission
    const appearanceForm = document.getElementById('appearance-form');
    if (appearanceForm) {
        appearanceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const theme = document.querySelector('input[name="theme"]:checked').id.replace('theme-', '');
            const dashboardRefresh = document.getElementById('dashboard-refresh').value;
            
            // Save settings to localStorage
            localStorage.setItem('theme', theme);
            localStorage.setItem('dashboardRefresh', dashboardRefresh);
            
            // Apply theme immediately
            applyTheme(theme);
            
            // Send data to server
            fetch('/api/user-preferences/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    type: 'appearance',
                    theme: theme,
                    dashboard_refresh: dashboardRefresh
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                } else {
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Appearance settings saved locally. Server sync failed.', 'warning');
            });
        });
    }
    
    // System Settings Form Submission (Admin only)
    const systemSettingsForm = document.getElementById('system-settings-form');
    if (systemSettingsForm) {
        systemSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const backupFrequency = document.getElementById('backup-frequency').value;
            const logRetention = document.getElementById('log-retention').value;
            
            // Send data to server
            fetch('/api/user-preferences/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    type: 'system',
                    backup_frequency: backupFrequency,
                    log_retention: logRetention
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert(data.message, 'success');
                    
                    // Also save to localStorage as fallback
                    localStorage.setItem('backup_frequency', backupFrequency);
                    localStorage.setItem('log_retention', logRetention);
                } else {
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('System settings saved locally. Server sync failed.', 'warning');
                
                // Save to localStorage as fallback
                localStorage.setItem('backup_frequency', backupFrequency);
                localStorage.setItem('log_retention', logRetention);
            });
        });
        
        // Load saved system settings from localStorage
        const savedBackupFrequency = localStorage.getItem('backup_frequency');
        const savedLogRetention = localStorage.getItem('log_retention');
        
        if (savedBackupFrequency) {
            document.getElementById('backup-frequency').value = savedBackupFrequency;
        }
        
        if (savedLogRetention) {
            document.getElementById('log-retention').value = savedLogRetention;
        }
    }
    
    // Network Thresholds
    const addThresholdBtn = document.getElementById('add-threshold-btn');
    if (addThresholdBtn) {
        addThresholdBtn.addEventListener('click', function() {
            // Reset the form
            document.getElementById('threshold-form').reset();
            document.getElementById('threshold-id').value = '';
            document.getElementById('threshold-modal-title').textContent = 'Add Network Threshold';
            
            // Show the modal
            const thresholdModal = new bootstrap.Modal(document.getElementById('threshold-modal'));
            thresholdModal.show();
        });
    }
    
    // Load thresholds from server
    function loadThresholds() {
        fetch('/api/thresholds/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const thresholdsTable = document.getElementById('thresholds-table').querySelector('tbody');
                thresholdsTable.innerHTML = '';
                
                if (data.thresholds.length === 0) {
                    const emptyRow = document.createElement('tr');
                    emptyRow.innerHTML = '<td colspan="4" class="text-center">No thresholds defined</td>';
                    thresholdsTable.appendChild(emptyRow);
                } else {
                    data.thresholds.forEach(threshold => {
                        const row = document.createElement('tr');
                        row.dataset.id = threshold.id;
                        
                        row.innerHTML = `
                            <td>${threshold.metric_display}</td>
                            <td>${threshold.threshold_value}%</td>
                            <td>
                                <span class="badge ${threshold.severity === 'warning' ? 'bg-warning' : threshold.severity === 'critical' ? 'bg-danger' : 'bg-dark'}">
                                    ${threshold.severity_display}
                                </span>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary edit-threshold-btn">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger delete-threshold-btn">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        `;
                        
                        thresholdsTable.appendChild(row);
                    });
                    
                    // Attach event listeners to new buttons
                    attachThresholdButtonListeners();
                }
            } else {
                showAlert(data.message || 'Failed to load thresholds', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to load thresholds. Please refresh the page.', 'danger');
        });
    }
    
    // Attach event listeners to threshold buttons
    function attachThresholdButtonListeners() {
        // Edit Threshold buttons
        document.querySelectorAll('.edit-threshold-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const row = this.closest('tr');
                const thresholdId = row.dataset.id;
                
                // Fetch threshold data from server
                fetch(`/api/thresholds/?id=${thresholdId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Populate form with threshold data from table
                        document.getElementById('threshold-id').value = thresholdId;
                        document.getElementById('metric').value = row.cells[0].textContent.toLowerCase().replace(/ /g, '_');
                        document.getElementById('threshold-value').value = row.cells[1].textContent.replace('%', '');
                        document.getElementById('severity').value = row.cells[2].querySelector('.badge').textContent.toLowerCase().trim();
                        
                        // Update modal title
                        document.getElementById('threshold-modal-title').textContent = 'Edit Network Threshold';
                        
                        // Show the modal
                        const thresholdModal = new bootstrap.Modal(document.getElementById('threshold-modal'));
                        thresholdModal.show();
                    } else {
                        showAlert(data.message || 'Failed to load threshold details', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Failed to load threshold details. Please try again.', 'danger');
                });
            });
        });
        
        // Delete Threshold buttons
        document.querySelectorAll('.delete-threshold-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this threshold?')) {
                    const row = this.closest('tr');
                    const thresholdId = row.dataset.id;
                    
                    fetch('/api/thresholds/', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            id: thresholdId
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            row.remove();
                            
                            // If no thresholds left, show the empty message
                            if (document.getElementById('thresholds-table').querySelector('tbody').children.length === 0) {
                                const emptyRow = document.createElement('tr');
                                emptyRow.innerHTML = '<td colspan="4" class="text-center">No thresholds defined</td>';
                                document.getElementById('thresholds-table').querySelector('tbody').appendChild(emptyRow);
                            }
                            
                            showAlert('Threshold deleted successfully', 'success');
                        } else {
                            showAlert(data.message || 'Failed to delete threshold', 'danger');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showAlert('Failed to delete threshold. Please try again.', 'danger');
                    });
                }
            });
        });
    }
    
    // Trigger load thresholds if on thresholds tab
    if (document.getElementById('thresholds-table')) {
        loadThresholds();
    }
    
    // Save Threshold button in modal
    const saveThresholdBtn = document.getElementById('save-threshold-btn');
    if (saveThresholdBtn) {
        saveThresholdBtn.addEventListener('click', function() {
            const thresholdId = document.getElementById('threshold-id').value;
            const metric = document.getElementById('metric').value;
            const thresholdValue = document.getElementById('threshold-value').value;
            const severity = document.getElementById('severity').value;
            
            // Validate form
            if (!metric || !thresholdValue || !severity) {
                showAlert('Please fill in all fields', 'danger');
                return;
            }
            
            const data = {
                metric: metric,
                threshold_value: thresholdValue,
                severity: severity
            };
            
            let method = 'POST';
            
            // If editing existing threshold, add ID and use PUT method
            if (thresholdId) {
                data.id = thresholdId;
                method = 'PUT';
            }
            
            // Send data to server
            fetch('/api/thresholds/', {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Hide the modal
                    const thresholdModal = bootstrap.Modal.getInstance(document.getElementById('threshold-modal'));
                    thresholdModal.hide();
                    
                    showAlert(thresholdId ? 'Threshold updated successfully' : 'Threshold created successfully', 'success');
                    
                    // Reload thresholds
                    loadThresholds();
                } else {
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Failed to save threshold. Please try again.', 'danger');
            });
        });
    }
    
    // User Management (Admin only)
    // Load users
    function loadUsers() {
        fetch('/api/users/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const usersTable = document.getElementById('users-table').querySelector('tbody');
                usersTable.innerHTML = '';
                
                if (data.users.length === 0) {
                    const emptyRow = document.createElement('tr');
                    emptyRow.innerHTML = '<td colspan="5" class="text-center">No users found</td>';
                    usersTable.appendChild(emptyRow);
                } else {
                    data.users.forEach(user => {
                        const row = document.createElement('tr');
                        row.dataset.id = user.id;
                        
                        row.innerHTML = `
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.role.charAt(0).toUpperCase() + user.role.slice(1)}</td>
                            <td>${user.last_login || 'Never'}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary edit-user-btn">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger delete-user-btn">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        `;
                        
                        usersTable.appendChild(row);
                    });
                    
                    // Attach event listeners to new buttons
                    attachUserButtonListeners();
                }
            } else {
                showAlert(data.message || 'Failed to load users', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to load users. Please refresh the page.', 'danger');
        });
    }
      // Attach event listeners to user buttons
    function attachUserButtonListeners() {
        // Edit User buttons
        document.querySelectorAll('.edit-user-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const row = this.closest('tr');
                const userId = row.dataset.id;
                
                // Fetch user data from server
                fetch(`/api/users/?id=${userId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Find the user in the response
                        const user = data.users.find(u => u.id.toString() === userId);
                        
                        if (user) {
                            // Create or get edit user modal
                            let editUserModal = document.getElementById('edit-user-modal');
                            
                            // If modal doesn't exist, create it
                            if (!editUserModal) {
                                const modalHTML = `
                                    <div class="modal fade" id="edit-user-modal" tabindex="-1" aria-hidden="true">
                                        <div class="modal-dialog">
                                            <div class="modal-content">
                                                <div class="modal-header">
                                                    <h5 class="modal-title">Edit User</h5>
                                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                                </div>
                                                <div class="modal-body">
                                                    <form id="edit-user-form">
                                                        <input type="hidden" id="edit-user-id">
                                                        <div class="mb-3">
                                                            <label for="edit-username" class="form-label">Username</label>
                                                            <input type="text" class="form-control" id="edit-username" disabled>
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="edit-email" class="form-label">Email</label>
                                                            <input type="email" class="form-control" id="edit-email" required>
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="edit-password" class="form-label">New Password (leave blank to keep current)</label>
                                                            <input type="password" class="form-control" id="edit-password">
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="edit-role" class="form-label">Role</label>
                                                            <select class="form-select" id="edit-role" required>
                                                                <option value="user">Normal User</option>
                                                                <option value="admin">Administrator</option>
                                                            </select>
                                                        </div>
                                                    </form>
                                                </div>
                                                <div class="modal-footer">
                                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                                    <button type="button" class="btn btn-primary" id="update-user-btn">Save Changes</button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                                
                                // Append modal to body
                                document.body.insertAdjacentHTML('beforeend', modalHTML);
                                
                                // Add event listener to save button
                                document.getElementById('update-user-btn').addEventListener('click', function() {
                                    const userId = document.getElementById('edit-user-id').value;
                                    const email = document.getElementById('edit-email').value;
                                    const password = document.getElementById('edit-password').value;
                                    const role = document.getElementById('edit-role').value;
                                    
                                    // Validate form
                                    if (!email || !role) {
                                        showAlert('Please fill in all required fields', 'danger');
                                        return;
                                    }
                                    
                                    // Prepare data for update
                                    const userData = {
                                        id: userId,
                                        email: email,
                                        role: role
                                    };
                                    
                                    // Add password only if provided
                                    if (password) {
                                        userData.password = password;
                                    }
                                    
                                    // Send data to server
                                    fetch('/api/users/', {
                                        method: 'PUT',
                                        headers: {
                                            'Content-Type': 'application/json',
                                            'X-CSRFToken': getCookie('csrftoken')
                                        },
                                        body: JSON.stringify(userData)
                                    })
                                    .then(response => response.json())
                                    .then(data => {
                                        if (data.status === 'success') {
                                            // Hide the modal
                                            const editUserModal = bootstrap.Modal.getInstance(document.getElementById('edit-user-modal'));
                                            editUserModal.hide();
                                            
                                            showAlert('User updated successfully', 'success');
                                            
                                            // Reload users
                                            loadUsers();
                                        } else {
                                            showAlert(data.message || 'An error occurred', 'danger');
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Error:', error);
                                        showAlert('Failed to update user. Please try again.', 'danger');
                                    });
                                });
                                
                                editUserModal = document.getElementById('edit-user-modal');
                            }
                            
                            // Populate form with user data
                            document.getElementById('edit-user-id').value = user.id;
                            document.getElementById('edit-username').value = user.username;
                            document.getElementById('edit-email').value = user.email;
                            document.getElementById('edit-password').value = '';
                            document.getElementById('edit-role').value = user.role;
                            
                            // Show the modal
                            const modal = new bootstrap.Modal(editUserModal);
                            modal.show();
                        } else {
                            showAlert('User not found', 'danger');
                        }
                    } else {
                        showAlert(data.message || 'Failed to load user details', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Failed to load user details. Please try again.', 'danger');
                });
            });
        });
        
        // Delete User buttons
        document.querySelectorAll('.delete-user-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
                    const row = this.closest('tr');
                    const userId = row.dataset.id;
                    
                    fetch('/api/users/', {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            id: userId
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            row.remove();
                            
                            // If no users left, show the empty message
                            if (document.getElementById('users-table').querySelector('tbody').children.length === 0) {
                                const emptyRow = document.createElement('tr');
                                emptyRow.innerHTML = '<td colspan="5" class="text-center">No users found</td>';
                                document.getElementById('users-table').querySelector('tbody').appendChild(emptyRow);
                            }
                            
                            showAlert('User deleted successfully', 'success');
                        } else {
                            showAlert(data.message || 'Failed to delete user', 'danger');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showAlert('Failed to delete user. Please try again.', 'danger');
                    });
                }
            });
        });
    }
    
    // Add User button
    const addUserBtn = document.getElementById('add-user-btn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', function() {
            // Reset the form
            document.getElementById('user-form').reset();
            
            // Show the modal
            const userModal = new bootstrap.Modal(document.getElementById('user-modal'));
            userModal.show();
        });
        
        // Trigger load users
        loadUsers();
    }      // Save User button in modal
    const saveUserBtn = document.getElementById('save-user-btn');
    if (saveUserBtn) {
        saveUserBtn.addEventListener('click', function() {
            // Get form values directly from the form elements
            const usernameInput = document.getElementById('new-username');
            const emailInput = document.getElementById('new-email');
            const passwordInput = document.getElementById('new-password');
            const roleInput = document.getElementById('new-role');
            
            // Check if elements exist before trying to access their values
            if (!usernameInput || !emailInput || !passwordInput || !roleInput) {
                console.error('Form elements not found:', {
                    usernameInput: !!usernameInput,
                    emailInput: !!emailInput,
                    passwordInput: !!passwordInput,
                    roleInput: !!roleInput
                });
                showAlert('Error: Form elements not found. Please try again.', 'danger');
                return;
            }
            
            const username = usernameInput.value.trim();
            const email = emailInput.value.trim();
            const password = passwordInput.value.trim();
            const role = roleInput.value.trim();
            
            // Debug information
            console.log('User form values:', {
                username: username,
                email: email,
                password: password ? 'Password provided (length: ' + password.length + ')' : 'No password',
                role: role
            });
            
            // More detailed validation
            if (!username) {
                showAlert('Username is required', 'danger');
                usernameInput.focus();
                return;
            }
            
            if (!email) {
                showAlert('Email is required', 'danger');
                emailInput.focus();
                return;
            }
            
            if (!password) {
                showAlert('Password is required', 'danger');
                passwordInput.focus();
                return;
            }
            
            if (!role) {
                showAlert('Role is required', 'danger');
                roleInput.focus();
                return;
            }
            
            // Send data to server
            fetch('/api/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: password,
                    role: role
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Hide the modal
                    const userModal = bootstrap.Modal.getInstance(document.getElementById('user-modal'));
                    userModal.hide();
                    
                    showAlert('User added successfully', 'success');
                    
                    // Reload users
                    loadUsers();
                } else {
                    showAlert(data.message || 'An error occurred', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Failed to add user. Please try again.', 'danger');
            });
        });
    }
    
    // Load current theme and preferences
    loadCurrentTheme();
});


// Show Bootstrap Alert
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find the tab content that's currently active
    const activeTab = document.querySelector('.tab-pane.active');
    if (activeTab) {
        activeTab.insertBefore(alertDiv, activeTab.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Apply Theme
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    } else if (theme === 'light') {
        document.body.classList.remove('dark-mode');
    } else if (theme === 'system') {
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }
}

// Load Current Theme
function loadCurrentTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const dashboardRefresh = localStorage.getItem('dashboardRefresh') || '30';
    
    // Update the form
    const themeElement = document.getElementById(`theme-${savedTheme}`);
    if (themeElement) {
        themeElement.checked = true;
    }
    
    const refreshElement = document.getElementById('dashboard-refresh');
    if (refreshElement) {
        refreshElement.value = dashboardRefresh;
    }
    
    // Apply the theme
    applyTheme(savedTheme);
}

// Get CSRF Token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
