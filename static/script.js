// Global variables
let selectedFile = null;
let selectedVideo = null;
let detectionInterval = null;
let streamInterval = null;
let isStreaming = false;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const detectBtn = document.getElementById('detectBtn');
const resultsSection = document.getElementById('resultsSection');
const resultImage = document.getElementById('resultImage');
const detectionList = document.getElementById('detectionList');
const loadingOverlay = document.getElementById('loadingOverlay');

// Video elements
const videoUploadArea = document.getElementById('videoUploadArea');
const videoInput = document.getElementById('videoInput');
const videoFileInfo = document.getElementById('videoFileInfo');
const videoFileName = document.getElementById('videoFileName');
const videoDetectBtn = document.getElementById('videoDetectBtn');

// Stream elements
const streamImage = document.getElementById('streamImage');

// Confidence elements
const confidenceSlider = document.getElementById('confidenceSlider');
const confidenceValue = document.getElementById('confidenceValue');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    startStatsUpdate();
    setupConfidenceSlider();
});

// Setup event listeners
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    videoInput.addEventListener('change', handleVideoSelect);
    
    // Drag and drop events for images
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Drag and drop events for videos
    videoUploadArea.addEventListener('dragover', handleVideoDragOver);
    videoUploadArea.addEventListener('dragleave', handleVideoDragLeave);
    videoUploadArea.addEventListener('drop', handleVideoDrop);
    videoUploadArea.addEventListener('click', () => videoInput.click());
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        videoUploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
}

// Prevent default drag behaviors
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processSelectedFile(file);
    }
}

// Handle drag over
function handleDragOver(e) {
    preventDefaults(e);
    uploadArea.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(e) {
    preventDefaults(e);
    uploadArea.classList.remove('dragover');
}

// Handle drop
function handleDrop(e) {
    preventDefaults(e);
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processSelectedFile(files[0]);
    }
}

// Process selected file
function processSelectedFile(file) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Tipe file tidak didukung. Gunakan JPG, PNG, atau GIF.', 'error');
        return;
    }
    
    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showNotification('Ukuran file terlalu besar. Maksimal 16MB.', 'error');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'flex';
    
    // Hide previous results
    resultsSection.style.display = 'none';
    
    showNotification('File berhasil dipilih. Klik "Deteksi" untuk memulai.', 'success');
}

// Detect image
async function detectImage() {
    if (!selectedFile) {
        showNotification('Pilih file terlebih dahulu.', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
            updateStats();
            showNotification('Deteksi berhasil!', 'success');
        } else {
            showNotification(result.error || 'Terjadi kesalahan saat deteksi.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Terjadi kesalahan pada jaringan.', 'error');
    } finally {
        showLoading(false);
    }
}

// Display detection results
function displayResults(result) {
    // Display result image
    resultImage.src = `data:image/jpeg;base64,${result.image}`;
    
    // Display detection list
    detectionList.innerHTML = '';
    
    if (result.detections.length === 0) {
        detectionList.innerHTML = '<p style="color: #718096; font-style: italic;">Tidak ada objek terdeteksi.</p>';
    } else {
        result.detections.forEach(detection => {
            const detectionItem = document.createElement('div');
            detectionItem.className = 'detection-item';
            detectionItem.innerHTML = `
                <div class="detection-class">${detection.class}</div>
                <div class="detection-confidence">Confidence: ${(detection.confidence * 100).toFixed(1)}%</div>
            `;
            detectionList.appendChild(detectionItem);
        });
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Show/hide loading overlay
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// Show notification
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
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1001;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Get notification icon
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

// Get notification color
function getNotificationColor(type) {
    switch (type) {
        case 'success': return '#48bb78';
        case 'error': return '#f56565';
        case 'warning': return '#ed8936';
        default: return '#4299e1';
    }
}

// Start stats update interval
function startStatsUpdate() {
    // Update stats every 5 seconds
    detectionInterval = setInterval(updateStats, 5000);
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/stats');
        const stats = await response.json();
        
        // Update total detections
        document.getElementById('totalDetections').textContent = stats.total_detections;
        
        // Update class counts
        Object.keys(stats.class_counts).forEach(className => {
            const elementId = `count-${className.replace(' ', '-')}`;
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = stats.class_counts[className];
            }
        });
        
        // Update recent activity
        updateRecentActivity(stats.recent_detections);
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update recent activity
function updateRecentActivity(recentDetections) {
    const recentActivity = document.getElementById('recentActivity');
    if (!recentActivity) return;
    
    // Get last 5 activities
    const lastActivities = recentDetections.slice(-5);
    
    recentActivity.innerHTML = '';
    
    lastActivities.forEach(activity => {
        const time = new Date(activity.timestamp).toLocaleTimeString('id-ID', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <span class="activity-time">${time}</span>
            <span class="activity-desc">${activity.total} deteksi</span>
        `;
        recentActivity.appendChild(activityItem);
    });
}

// Setup confidence slider
function setupConfidenceSlider() {
    confidenceSlider.addEventListener('input', function() {
        confidenceValue.textContent = this.value + '%';
    });
}

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.getElementById('imageTab').style.display = 'none';
    document.getElementById('videoTab').style.display = 'none';
    document.getElementById('streamTab').style.display = 'none';
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').style.display = 'block';
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Video handling functions
function handleVideoSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processSelectedVideo(file);
    }
}

function handleVideoDragOver(e) {
    preventDefaults(e);
    videoUploadArea.classList.add('dragover');
}

function handleVideoDragLeave(e) {
    preventDefaults(e);
    videoUploadArea.classList.remove('dragover');
}

function handleVideoDrop(e) {
    preventDefaults(e);
    videoUploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processSelectedVideo(files[0]);
    }
}

function processSelectedVideo(file) {
    // Validate file type
    const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/wmv', 'video/flv'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Tipe file video tidak didukung. Gunakan MP4, AVI, MOV, MKV, WMV, atau FLV.', 'error');
        return;
    }
    
    // Validate file size (100MB max for video)
    if (file.size > 100 * 1024 * 1024) {
        showNotification('Ukuran file video terlalu besar. Maksimal 100MB.', 'error');
        return;
    }
    
    selectedVideo = file;
    videoFileName.textContent = file.name;
    videoFileInfo.style.display = 'flex';
    
    showNotification('Video berhasil dipilih. Klik "Process Video" untuk memulai.', 'success');
}

// Video detection
async function detectVideo() {
    if (!selectedVideo) {
        showNotification('Pilih video terlebih dahulu.', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('video', selectedVideo);
        formData.append('confidence_threshold', confidenceSlider.value / 100);
        
        const response = await fetch('/video-inference', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayVideoResults(result);
            showNotification('Video processing berhasil!', 'success');
        } else {
            showNotification(result.error || 'Terjadi kesalahan saat processing video.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Terjadi kesalahan pada jaringan.', 'error');
    } finally {
        showLoading(false);
    }
}

function displayVideoResults(result) {
    // Display video preview
    resultImage.src = `data:image/jpeg;base64,${result.preview}`;
    resultsSection.style.display = 'block';
    
    // Update detection list
    detectionList.innerHTML = '<p style="color: #718096; font-style: italic;">Video processing completed. Check results folder for processed video.</p>';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Stream functions
function startStream() {
    if (isStreaming) return;
    
    isStreaming = true;
    streamImage.style.display = 'block';
    streamImage.src = '/video_feed';
    
    // Show stop button
    document.querySelector('.stream-btn').style.display = 'none';
    document.querySelector('.stream-btn.stop').style.display = 'inline-flex';
    
    showNotification('Stream started!', 'success');
}

function stopStream() {
    if (!isStreaming) return;
    
    isStreaming = false;
    streamImage.style.display = 'none';
    streamImage.src = '';
    
    // Show start button
    document.querySelector('.stream-btn').style.display = 'inline-flex';
    document.querySelector('.stream-btn.stop').style.display = 'none';
    
    showNotification('Stream stopped!', 'info');
}

// Reset statistics
async function resetStats() {
    // Konfirmasi sebelum reset
    if (!confirm('Apakah Anda yakin ingin mereset semua statistik dan menghapus semua file? Tindakan ini tidak dapat dibatalkan.')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/reset', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Reset UI elements
            selectedFile = null;
            selectedVideo = null;
            
            // Clear file inputs
            fileInput.value = '';
            videoInput.value = '';
            
            // Hide file info sections
            fileInfo.style.display = 'none';
            videoFileInfo.style.display = 'none';
            
            // Hide results section
            resultsSection.style.display = 'none';
            
            // Reset confidence slider
            confidenceSlider.value = 50;
            confidenceValue.textContent = '50%';
            
            // Update stats display
            updateStats();
            
            showNotification('Statistik berhasil direset!', 'success');
        } else {
            showNotification(result.error || 'Terjadi kesalahan saat reset.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Terjadi kesalahan pada jaringan.', 'error');
    } finally {
        showLoading(false);
    }
}

// Update detectImage function to include confidence threshold
async function detectImage() {
    if (!selectedFile) {
        showNotification('Pilih file terlebih dahulu.', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('confidence_threshold', confidenceSlider.value / 100);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
            updateStats();
            showNotification('Deteksi berhasil!', 'success');
        } else {
            showNotification(result.error || 'Terjadi kesalahan saat deteksi.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Terjadi kesalahan pada jaringan.', 'error');
    } finally {
        showLoading(false);
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (detectionInterval) {
        clearInterval(detectionInterval);
    }
    if (streamInterval) {
        clearInterval(streamInterval);
    }
    if (isStreaming) {
        stopStream();
    }
});
