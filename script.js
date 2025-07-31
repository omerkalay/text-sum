// AI Summarizer - Modern JavaScript

const API_BASE_URL = 'https://text-sum-7t11.onrender.com'; // Your actual backend URL

// DOM Elements
const pdfForm = document.getElementById('pdf-form');
const textForm = document.getElementById('text-form');
const loadingOverlay = document.getElementById('loading');
const resultSection = document.getElementById('result');
const summaryText = document.getElementById('summary-text');
const originalLength = document.getElementById('original-length');
const summaryLength = document.getElementById('summary-length');
const reductionPercentage = document.getElementById('reduction-percentage');
const inputText = document.getElementById('input-text');
const charCount = document.querySelector('.char-count');
const fileUploadArea = document.getElementById('file-upload-area');

// Global variables
let currentSummary = '';
let currentOriginalText = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Initialize character counter
    updateCharCount();
    
    // Set up drag and drop for file upload
    setupDragAndDrop();
    
    // Check for saved theme preference
    loadThemePreference();
}

function setupEventListeners() {
    // Form submissions
    pdfForm.addEventListener('submit', handlePdfSubmit);
    textForm.addEventListener('submit', handleTextSubmit);
    
    // Character counter
    inputText.addEventListener('input', updateCharCount);
    
    // File input change
    document.getElementById('pdf-file').addEventListener('change', handleFileSelect);
}

function setupDragAndDrop() {
    const uploadArea = document.querySelector('.upload-placeholder');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        uploadArea.style.borderColor = 'var(--accent-primary)';
        uploadArea.style.background = 'rgba(0, 212, 255, 0.1)';
    }
    
    function unhighlight(e) {
        uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        uploadArea.style.background = 'var(--bg-tertiary)';
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const file = files[0];
            if (file.type === 'application/pdf') {
                document.getElementById('pdf-file').files = files;
                handleFileSelect();
            } else {
                showNotification('Please select a PDF file', 'error');
            }
        }
    }
}

function handleFileSelect() {
    const fileInput = document.getElementById('pdf-file');
    const file = fileInput.files[0];
    
    if (file) {
        const uploadPlaceholder = document.querySelector('.upload-placeholder');
        uploadPlaceholder.innerHTML = `
            <i class="fas fa-file-pdf"></i>
            <span>${file.name}</span>
            <small>${formatFileSize(file.size)}</small>
        `;
        uploadPlaceholder.style.borderColor = 'var(--accent-success)';
        uploadPlaceholder.style.background = 'rgba(0, 255, 136, 0.1)';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateCharCount() {
    const count = inputText.value.length;
    charCount.textContent = `${count} characters`;
    
    // Change color based on length
    if (count > 10000) {
        charCount.style.color = 'var(--accent-warning)';
    } else if (count > 5000) {
        charCount.style.color = 'var(--accent-primary)';
    } else {
        charCount.style.color = 'var(--text-muted)';
    }
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.tab-btn').classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Reset forms
    resetForms();
}

function resetForms() {
    pdfForm.reset();
    textForm.reset();
    inputText.value = '';
    updateCharCount();
    
    // Reset file upload area
    const uploadPlaceholder = document.querySelector('.upload-placeholder');
    uploadPlaceholder.innerHTML = `
        <i class="fas fa-file-pdf"></i>
        <span>Choose PDF file</span>
        <small>or drag and drop here</small>
    `;
    uploadPlaceholder.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    uploadPlaceholder.style.background = 'var(--bg-tertiary)';
    
    // Hide result section
    resultSection.style.display = 'none';
}

// Form handlers
async function handlePdfSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdf-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a PDF file', 'error');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showNotification('File size must be less than 10MB', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    await submitSummary(formData, 'pdf');
}

async function handleTextSubmit(e) {
    e.preventDefault();
    
    const text = inputText.value.trim();
    const maxLength = document.getElementById('max-length').value;
    
    if (!text) {
        showNotification('Please enter some text', 'error');
        return;
    }
    
    if (text.length < 50) {
        showNotification('Text must be at least 50 characters long', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('text', text);
    formData.append('max_length', maxLength);
    
    await submitSummary(formData, 'text');
}

async function submitSummary(formData, type) {
    try {
        showLoading(true);
        
        const endpoint = type === 'pdf' ? '/summarize-pdf' : '/summarize-text';
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayResult(data);
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayResult(data) {
    currentSummary = data.summary;
    currentOriginalText = data.original_text;
    
    // Update summary text
    summaryText.textContent = data.summary;
    
    // Update statistics
    const originalWords = data.original_length;
    const summaryWords = data.summary_length;
    const reduction = Math.round(((originalWords - summaryWords) / originalWords) * 100);
    
    originalLength.textContent = `${originalWords} words`;
    summaryLength.textContent = `${summaryWords} words`;
    reductionPercentage.textContent = `${reduction}%`;
    
    // Show result section
    resultSection.style.display = 'block';
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });
    
    // Show success notification
    showNotification('Summary generated successfully!', 'success');
}

function showLoading(show) {
    if (show) {
        loadingOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    } else {
        loadingOverlay.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Result actions
function downloadSummary() {
    if (!currentSummary) return;
    
    const blob = new Blob([currentSummary], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'summary.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Summary downloaded!', 'success');
}

async function copySummary() {
    if (!currentSummary) return;
    
    try {
        await navigator.clipboard.writeText(currentSummary);
        showNotification('Summary copied to clipboard!', 'success');
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = currentSummary;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Summary copied to clipboard!', 'success');
    }
}

function newSummary() {
    resetForms();
    showNotification('Ready for new summary!', 'info');
}

function closeResult() {
    resultSection.style.display = 'none';
}

// Theme toggle
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme toggle icon
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = newTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
}

function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = savedTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-card);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-lg);
        padding: var(--spacing-md);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        max-width: 400px;
    `;
    
    // Add notification content styles
    const content = notification.querySelector('.notification-content');
    content.style.cssText = `
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        color: var(--text-primary);
    `;
    
    // Add icon styles
    const icon = notification.querySelector('i');
    icon.style.color = getNotificationColor(type);
    
    // Add close button styles
    const closeBtn = notification.querySelector('button');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: var(--spacing-xs);
        border-radius: var(--radius-sm);
        transition: var(--transition-normal);
        margin-left: auto;
    `;
    
    closeBtn.addEventListener('mouseenter', () => {
        closeBtn.style.background = 'var(--bg-tertiary)';
        closeBtn.style.color = 'var(--text-primary)';
    });
    
    closeBtn.addEventListener('mouseleave', () => {
        closeBtn.style.background = 'none';
        closeBtn.style.color = 'var(--text-secondary)';
    });
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

function getNotificationColor(type) {
    const colors = {
        success: 'var(--accent-success)',
        error: 'var(--accent-error)',
        warning: 'var(--accent-warning)',
        info: 'var(--accent-primary)'
    };
    return colors[type] || colors.info;
}

// Footer functions
function showAbout() {
    showNotification('AI Summarizer - Powered by Hugging Face AI models for intelligent text summarization.', 'info');
}

function showPrivacy() {
    showNotification('Your data is processed securely and not stored permanently.', 'info');
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 