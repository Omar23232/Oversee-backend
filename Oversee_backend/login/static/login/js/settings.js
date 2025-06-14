
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
            showAlert('Profile update functionality will be implemented soon!', 'info');
        });
    }
    
    // Password Form Submission
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            // Validate passwords match
            if (newPassword !== confirmPassword) {
                showAlert('New passwords do not match!', 'danger');
                return;
            }
            
            showAlert('Password change functionality will be implemented soon!', 'info');
            passwordForm.reset();
        });
    }
    
    // Notification Form Submission
    const notificationForm = document.getElementById('notification-form');
    if (notificationForm) {
        notificationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showAlert('Notification settings saved to local storage', 'info');
            
            // Save to localStorage for demo purposes
            localStorage.setItem('browser_notifications', document.getElementById('browser-notifications').checked);
            localStorage.setItem('email_notifications', document.getElementById('email-notifications').checked);
            localStorage.setItem('notification_frequency', document.querySelector('input[name="notification-frequency"]:checked').id);
        });
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
            
            showAlert('Appearance settings saved!', 'success');
        });
    }
    
    // System Settings Form Submission (Admin only)
    const systemSettingsForm = document.getElementById('system-settings-form');
    if (systemSettingsForm) {
        systemSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Save to localStorage for demo purposes
            localStorage.setItem('backup_frequency', document.getElementById('backup-frequency').value);
            localStorage.setItem('log_retention', document.getElementById('log-retention').value);
            
            showAlert('System settings saved to local storage', 'info');
        });
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
    
    // Edit Threshold buttons
    const editThresholdBtns = document.querySelectorAll('.edit-threshold-btn');
    editThresholdBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const thresholdId = row.dataset.id;
            
            // For demo purposes, populate with dummy data
            document.getElementById('threshold-id').value = thresholdId;
            document.getElementById('metric').value = row.cells[0].textContent.toLowerCase().replace(' ', '_');
            document.getElementById('threshold-value').value = row.cells[1].textContent.replace('%', '');
            document.getElementById('severity').value = row.cells[2].querySelector('.badge').textContent.toLowerCase().trim();
            
            // Update modal title
            document.getElementById('threshold-modal-title').textContent = 'Edit Network Threshold';
            
            // Show the modal
            const thresholdModal = new bootstrap.Modal(document.getElementById('threshold-modal'));
            thresholdModal.show();
        });
    });
    
    // Delete Threshold buttons
    const deleteThresholdBtns = document.querySelectorAll('.delete-threshold-btn');
    deleteThresholdBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this threshold?')) {
                const row = this.closest('tr');
                
                row.remove();
                
                // If no thresholds left, show the empty message
                if (document.getElementById('thresholds-table').querySelector('tbody').children.length === 0) {
                    const emptyRow = document.createElement('tr');
                    emptyRow.innerHTML = '<td colspan="4" class="text-center">No thresholds defined</td>';
                    document.getElementById('thresholds-table').querySelector('tbody').appendChild(emptyRow);
                }
                
                showAlert('Threshold deleted!', 'success');
            }
        });
    });
    
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
            
            // For demo purposes, just show success message
            showAlert(thresholdId ? 'Threshold updated!' : 'New threshold added!', 'success');
            
            // Hide the modal
            const thresholdModal = bootstrap.Modal.getInstance(document.getElementById('threshold-modal'));
            thresholdModal.hide();
            
            // Reload the page to reset the demo
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
    
    // User Management (Admin only)
    const addUserBtn = document.getElementById('add-user-btn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', function() {
            // Reset the form
            document.getElementById('user-form').reset();
            
            // Show the modal
            const userModal = new bootstrap.Modal(document.getElementById('user-modal'));
            userModal.show();
        });
    }
    
    // Save User button in modal
    const saveUserBtn = document.getElementById('save-user-btn');
    if (saveUserBtn) {
        saveUserBtn.addEventListener('click', function() {
            const username = document.getElementById('new-username').value;
            const email = document.getElementById('new-email').value;
            const password = document.getElementById('new-password').value;
            const role = document.getElementById('new-role').value;
            
            // Validate form
            if (!username || !email || !password || !role) {
                showAlert('Please fill in all fields', 'danger');
                return;
            }
            
            // For demo purposes, just show success message
            showAlert('User added successfully!', 'success');
            
            // Hide the modal
            const userModal = bootstrap.Modal.getInstance(document.getElementById('user-modal'));
            userModal.hide();
        });
    }
    
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
