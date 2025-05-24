// Main JavaScript for College Notes & PYQs Portal

document.addEventListener('DOMContentLoaded', function() {
    console.log('College Notes & PYQs Portal loaded');
    
    // Initialize file upload functionality
    initializeFileUpload();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize animations
    initializeAnimations();
});

/**
 * Initialize file upload functionality
 */
function initializeFileUpload() {
    const fileInput = document.getElementById('files');
    const filePreview = document.getElementById('filePreview');
    const fileList = document.getElementById('fileList');
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadProgress = document.getElementById('uploadProgress');
    
    if (!fileInput) return;
    
    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        displayFilePreview(files);
    });
    
    // Handle form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const files = fileInput.files;
            if (files.length === 0) {
                e.preventDefault();
                showAlert('Please select at least one file to upload.', 'warning');
                return;
            }
            
            // Validate file sizes
            let hasLargeFile = false;
            const maxSize = 16 * 1024 * 1024; // 16MB
            
            Array.from(files).forEach(file => {
                if (file.size > maxSize) {
                    hasLargeFile = true;
                }
            });
            
            if (hasLargeFile) {
                e.preventDefault();
                showAlert('Some files are larger than 16MB. Please reduce file sizes and try again.', 'error');
                return;
            }
            
            // Show upload progress
            showUploadProgress();
        });
    }
    
    /**
     * Display preview of selected files
     */
    function displayFilePreview(files) {
        if (files.length === 0) {
            filePreview.style.display = 'none';
            return;
        }
        
        fileList.innerHTML = '';
        
        files.forEach((file, index) => {
            const fileItem = createFileItem(file, index);
            fileList.appendChild(fileItem);
        });
        
        filePreview.style.display = 'block';
        filePreview.classList.add('fade-in');
    }
    
    /**
     * Create file item element for preview
     */
    function createFileItem(file, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const fileIcon = getFileIcon(file.name);
        const fileSize = formatFileSize(file.size);
        const fileName = file.name.length > 40 ? file.name.substring(0, 40) + '...' : file.name;
        
        fileItem.innerHTML = `
            <div class="file-info">
                <div class="d-flex align-items-center">
                    <i class="fas ${fileIcon} me-2"></i>
                    <span class="fw-medium">${fileName}</span>
                </div>
                <small class="file-size">${fileSize}</small>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        return fileItem;
    }
    
    /**
     * Show upload progress
     */
    function showUploadProgress() {
        if (uploadProgress && uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
            uploadProgress.style.display = 'block';
            
            // Simulate progress (since we can't track real progress easily)
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 30;
                if (progress > 90) progress = 90;
                
                const progressBar = uploadProgress.querySelector('.progress-bar');
                progressBar.style.width = progress + '%';
                
                if (progress >= 90) {
                    clearInterval(interval);
                }
            }, 500);
        }
    }
}

/**
 * Get appropriate icon for file type
 */
function getFileIcon(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    
    const icons = {
        'pdf': 'fa-file-pdf text-danger',
        'doc': 'fa-file-word text-primary',
        'docx': 'fa-file-word text-primary',
        'txt': 'fa-file-alt text-secondary',
        'rtf': 'fa-file-alt text-secondary',
        'odt': 'fa-file-alt text-secondary',
        'ppt': 'fa-file-powerpoint text-warning',
        'pptx': 'fa-file-powerpoint text-warning',
        'xls': 'fa-file-excel text-success',
        'xlsx': 'fa-file-excel text-success',
        'csv': 'fa-file-excel text-success',
        'jpg': 'fa-file-image text-info',
        'jpeg': 'fa-file-image text-info',
        'png': 'fa-file-image text-info',
        'gif': 'fa-file-image text-info',
        'bmp': 'fa-file-image text-info',
        'zip': 'fa-file-archive text-purple',
        'rar': 'fa-file-archive text-purple',
        '7z': 'fa-file-archive text-purple',
        'tar': 'fa-file-archive text-purple',
        'gz': 'fa-file-archive text-purple'
    };
    
    return icons[extension] || 'fa-file text-secondary';
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Remove file from selection (placeholder function)
 */
function removeFile(index) {
    // This would require rebuilding the FileList, which is read-only
    // For now, just show a message
    showAlert('To remove files, please reselect your files.', 'info');
}

/**
 * Confirm delete action
 */
function confirmDelete(filename) {
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    document.getElementById('fileToDelete').textContent = filename;
    document.getElementById('confirmDeleteBtn').href = `/delete/${encodeURIComponent(filename)}`;
    modal.show();
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the main container
    const mainContainer = document.querySelector('main .container');
    if (mainContainer) {
        mainContainer.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = mainContainer.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

/**
 * Get icon for alert type
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-1px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Handle drag and drop file upload
 */
function initializeDragAndDrop() {
    const uploadArea = document.querySelector('.card-body');
    if (!uploadArea) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        uploadArea.classList.add('border-primary', 'bg-light');
    }
    
    function unhighlight(e) {
        uploadArea.classList.remove('border-primary', 'bg-light');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = document.getElementById('files');
        
        if (fileInput) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}

// Initialize drag and drop when DOM is ready
document.addEventListener('DOMContentLoaded', initializeDragAndDrop);

/**
 * Search functionality for files
 */
function initializeSearch() {
    const searchInput = document.getElementById('searchFiles');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const fileRows = document.querySelectorAll('tbody tr');
        
        fileRows.forEach(row => {
            const fileName = row.querySelector('td:first-child').textContent.toLowerCase();
            const isVisible = fileName.includes(searchTerm);
            row.style.display = isVisible ? '' : 'none';
        });
    });
}

// Additional utility functions
window.downloadFile = function(filename) {
    window.location.href = `/download/${encodeURIComponent(filename)}`;
};

// Error handling for images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.style.display = 'none';
    }
}, true);

// Handle offline/online status
window.addEventListener('online', function() {
    showAlert('Connection restored!', 'success');
});

window.addEventListener('offline', function() {
    showAlert('You are currently offline. Some features may not work.', 'warning');
});
