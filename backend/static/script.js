// Global variables
let currentSummary = '';
let originalText = '';

// Tab switching functionality
function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Hide any existing results
    hideResults();
}

// Show loading spinner
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
}

// Hide loading spinner
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Show results
function showResults(data) {
    const resultContainer = document.getElementById('result');
    const summaryText = document.getElementById('summary-text');
    const originalLength = document.getElementById('original-length');
    const summaryLength = document.getElementById('summary-length');
    
    currentSummary = data.summary;
    originalText = data.original_text;
    
    summaryText.textContent = data.summary;
    originalLength.textContent = `Original: ${data.original_length} words`;
    summaryLength.textContent = `Summary: ${data.summary_length} words`;
    
    resultContainer.style.display = 'block';
}

// Hide results
function hideResults() {
    document.getElementById('result').style.display = 'none';
}

// Show error message
function showError(message) {
    const resultContainer = document.getElementById('result');
    const summaryText = document.getElementById('summary-text');
    
    summaryText.innerHTML = `<div class="error">${message}</div>`;
    resultContainer.style.display = 'block';
}

// Download summary as text file
function downloadSummary() {
    if (!currentSummary) return;
    
    const blob = new Blob([currentSummary], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'summary.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Handle PDF form submission
document.getElementById('pdf-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdf-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a PDF file');
        return;
    }
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please select a valid PDF file');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/summarize-pdf', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to process PDF');
        }
        
        const data = await response.json();
        showResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while processing the PDF');
    } finally {
        hideLoading();
    }
});

// Handle text form submission
document.getElementById('text-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const textInput = document.getElementById('input-text');
    const maxLengthSelect = document.getElementById('max-length');
    const text = textInput.value.trim();
    const maxLength = parseInt(maxLengthSelect.value);
    
    if (!text) {
        showError('Please enter some text to summarize');
        return;
    }
    
    if (text.length < 50) {
        showError('Text must be at least 50 characters long');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('text', text);
    formData.append('max_length', maxLength);
    
    try {
        const response = await fetch('/summarize-text', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to summarize text');
        }
        
        const data = await response.json();
        showResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while summarizing the text');
    } finally {
        hideLoading();
    }
});

// File input change handler
document.getElementById('pdf-file').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const label = document.querySelector('.file-upload label');
    
    if (file) {
        label.textContent = `Selected: ${file.name}`;
        label.style.borderColor = '#28a745';
        label.style.backgroundColor = '#d4edda';
        label.style.color = '#155724';
    } else {
        label.textContent = 'Choose PDF file';
        label.style.borderColor = '#ddd';
        label.style.backgroundColor = '#f8f9fa';
        label.style.color = '#666';
    }
});

// Textarea character counter
document.getElementById('input-text').addEventListener('input', function(e) {
    const text = e.target.value;
    const charCount = text.length;
    const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
    
    // You can add a character/word counter display here if needed
    console.log(`Characters: ${charCount}, Words: ${wordCount}`);
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab.id === 'pdf-tab') {
            document.getElementById('pdf-form').dispatchEvent(new Event('submit'));
        } else if (activeTab.id === 'text-tab') {
            document.getElementById('text-form').dispatchEvent(new Event('submit'));
        }
    }
});

// Auto-resize textarea
document.getElementById('input-text').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 400) + 'px';
});

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Set initial tab
    switchTab('pdf');
    
    // Add some helpful tips
    console.log('AI Text Summarizer loaded successfully!');
    console.log('Tips:');
    console.log('- Use Ctrl/Cmd + Enter to quickly submit forms');
    console.log('- For best results, use text with at least 100 words');
    console.log('- PDF files should contain extractable text (not scanned images)');
}); 