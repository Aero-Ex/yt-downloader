// Initialize Socket.IO with better timeout and reconnection settings
const socket = io({
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity,
    timeout: 120000,  // 2 minutes timeout to match server
    transports: ['polling', 'websocket'],  // Use polling first (more stable for long downloads)
    upgrade: false  // Don't try to upgrade to websocket during active downloads
});

// State management
let currentDownloadId = null;
let currentVideoInfo = null;
let selectedFormatType = 'video';
let videoDurationSeconds = 0;
let isDragging = false;
let dragTarget = null;
let downloadStatusPollInterval = null;
let lastProgressUpdate = null;

// DOM Elements
const videoUrl = document.getElementById('videoUrl');
const fetchInfoBtn = document.getElementById('fetchInfoBtn');
const videoInfoSection = document.getElementById('videoInfoSection');
const downloadOptionsSection = document.getElementById('downloadOptionsSection');
const progressSection = document.getElementById('progressSection');
const completeSection = document.getElementById('completeSection');
const errorSection = document.getElementById('errorSection');

const videoThumbnail = document.getElementById('videoThumbnail');
const videoTitle = document.getElementById('videoTitle');
const videoUploader = document.getElementById('videoUploader');
const videoDuration = document.getElementById('videoDuration');

const formatTypeButtons = document.querySelectorAll('.btn-option');
const qualitySelect = document.getElementById('qualitySelect');
const formatSelect = document.getElementById('formatSelect');
const startTimeInput = document.getElementById('startTime');
const endTimeInput = document.getElementById('endTime');
const downloadBtn = document.getElementById('downloadBtn');

const progressBarFill = document.getElementById('progressBarFill');
const progressPercent = document.getElementById('progressPercent');
const progressSpeed = document.getElementById('progressSpeed');
const progressEta = document.getElementById('progressEta');
const progressStatus = document.getElementById('progressStatus');

const downloadedFileName = document.getElementById('downloadedFileName');
const downloadFileBtn = document.getElementById('downloadFileBtn');
const downloadAnotherBtn = document.getElementById('downloadAnotherBtn');
const tryAgainBtn = document.getElementById('tryAgainBtn');
const errorMessage = document.getElementById('errorMessage');

// Timeline elements
const timelineContainer = document.getElementById('timelineContainer');
const timelineTrack = document.getElementById('timelineTrack');
const timelineSelection = document.getElementById('timelineSelection');
const handleStart = document.getElementById('handleStart');
const handleEnd = document.getElementById('handleEnd');
const tooltipStart = document.getElementById('tooltipStart');
const tooltipEnd = document.getElementById('tooltipEnd');
const timelineTotalDuration = document.getElementById('timelineTotalDuration');
const selectedDuration = document.getElementById('selectedDuration');
const trimmingRange = document.getElementById('trimmingRange');
const toggleManualTime = document.getElementById('toggleManualTime');
const manualTimeInputs = document.getElementById('manualTimeInputs');

// Socket.IO Event Handlers
socket.on('connect', () => {
    console.log('Connected to server, Socket ID:', socket.id);
});

socket.on('disconnect', (reason) => {
    console.log('Disconnected from server. Reason:', reason);
    if (reason === 'io server disconnect') {
        // Server disconnected us, manually reconnect
        socket.connect();
    }
    // Otherwise, socket will automatically try to reconnect
});

socket.on('reconnect', (attemptNumber) => {
    console.log('Reconnected to server after', attemptNumber, 'attempts');
});

socket.on('reconnect_attempt', (attemptNumber) => {
    console.log('Attempting to reconnect...', attemptNumber);
});

socket.on('reconnect_error', (error) => {
    console.error('Reconnection error:', error);
});

socket.on('connect_error', (error) => {
    console.error('Socket connection error:', error);
});

socket.on('download_progress', (data) => {
    console.log('Download progress received:', data);
    lastProgressUpdate = Date.now();

    if (data.status === 'downloading') {
        progressPercent.textContent = data.percent;
        progressSpeed.textContent = `Speed: ${data.speed}`;
        progressEta.textContent = `ETA: ${data.eta}`;

        // Update progress bar
        const percentValue = parseFloat(data.percent);
        progressBarFill.style.width = percentValue + '%';

        progressStatus.textContent = `Downloading... ${data.downloaded} / ${data.total}`;
    } else if (data.status === 'processing') {
        progressStatus.textContent = data.message;
        progressBarFill.style.width = '100%';
    }
});

socket.on('download_complete', (data) => {
    console.log('Download complete received:', data);
    stopPollingDownloadStatus();
    currentDownloadId = data.download_id;
    showSection('complete');
    downloadedFileName.textContent = data.filename;
});

socket.on('download_error', (data) => {
    console.error('Download error received:', data);
    stopPollingDownloadStatus();
    showError(data.error);
});

// Optimized fallback polling - only poll if socket updates stop
async function pollDownloadStatus() {
    if (!currentDownloadId) return;

    // Only poll if we haven't received socket updates recently (10+ seconds)
    const timeSinceLastUpdate = lastProgressUpdate ? (Date.now() - lastProgressUpdate) : Infinity;
    if (timeSinceLastUpdate < 10000) {
        // Socket is working fine, no need to poll
        return;
    }

    try {
        const response = await fetch(`/api/download-status/${currentDownloadId}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();

        console.log('Polling download status:', data);

        if (data.status === 'completed') {
            stopPollingDownloadStatus();
            showSection('complete');
            downloadedFileName.textContent = data.filename;
        } else if (data.status === 'error') {
            stopPollingDownloadStatus();
            showError(data.error);
        } else if (data.status === 'downloading') {
            // Show that download is active even without socket updates
            progressStatus.textContent = 'Download in progress... Please wait';

            // Add a pulsing animation to progress bar to show activity
            if (!progressBarFill.classList.contains('pulsing')) {
                progressBarFill.classList.add('pulsing');
            }

            // If we're not getting socket updates, show indeterminate progress
            progressBarFill.style.width = '50%';
            progressStatus.textContent = 'Downloading... (waiting for progress updates)';
        }
    } catch (error) {
        console.error('Error polling download status:', error);
    }
}

function startPollingDownloadStatus() {
    console.log('Starting download status polling as fallback');
    stopPollingDownloadStatus(); // Clear any existing interval
    lastProgressUpdate = Date.now();
    // Poll every 5 seconds (less aggressive than before)
    downloadStatusPollInterval = setInterval(pollDownloadStatus, 5000);
}

function stopPollingDownloadStatus() {
    if (downloadStatusPollInterval) {
        console.log('Stopping download status polling');
        clearInterval(downloadStatusPollInterval);
        downloadStatusPollInterval = null;
        // Remove pulsing animation
        progressBarFill.classList.remove('pulsing');
    }
}

// Event Listeners
fetchInfoBtn.addEventListener('click', fetchVideoInfo);
downloadBtn.addEventListener('click', startDownload);
downloadAnotherBtn.addEventListener('click', reset);
tryAgainBtn.addEventListener('click', reset);

videoUrl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        fetchVideoInfo();
    }
});

formatTypeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        formatTypeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedFormatType = btn.dataset.type;

        // Update quality options based on format type
        updateQualityOptions(selectedFormatType);
    });
});

downloadFileBtn.addEventListener('click', () => {
    if (currentDownloadId) {
        window.location.href = `/api/download-file/${currentDownloadId}`;
    }
});

// Timeline event listeners
toggleManualTime.addEventListener('click', () => {
    manualTimeInputs.classList.toggle('hidden');
});

handleStart.addEventListener('mousedown', (e) => startDragging(e, 'start'));
handleEnd.addEventListener('mousedown', (e) => startDragging(e, 'end'));

document.addEventListener('mousemove', onDrag);
document.addEventListener('mouseup', stopDragging);

// Touch support for mobile
if (handleStart) {
    handleStart.addEventListener('touchstart', (e) => {
        console.log('Touch start on handleStart');
        e.preventDefault(); // Prevent scrolling while dragging
        e.stopPropagation(); // Stop event from bubbling
        startDragging(e.touches[0], 'start');
    }, { passive: false });
}

if (handleEnd) {
    handleEnd.addEventListener('touchstart', (e) => {
        console.log('Touch start on handleEnd');
        e.preventDefault(); // Prevent scrolling while dragging
        e.stopPropagation(); // Stop event from bubbling
        startDragging(e.touches[0], 'end');
    }, { passive: false });
}

document.addEventListener('touchmove', (e) => {
    if (isDragging) {
        console.log('Touch move:', e.touches[0].clientX);
        e.preventDefault(); // Prevent scrolling while dragging
        e.stopPropagation();
        onDrag(e.touches[0]);
    }
}, { passive: false });

document.addEventListener('touchend', (e) => {
    console.log('Touch end');
    stopDragging();
});

document.addEventListener('touchcancel', (e) => {
    console.log('Touch cancel');
    stopDragging();
});

// Manual time input sync
startTimeInput.addEventListener('input', syncTimelineFromInputs);
endTimeInput.addEventListener('input', syncTimelineFromInputs);

// Quality and Format Options Update
function updateQualityOptions(formatType) {
    const currentQualityValue = qualitySelect.value;
    const currentFormatValue = formatSelect.value;

    if (formatType === 'audio') {
        // Audio quality options (bitrate-based)
        qualitySelect.innerHTML = `
            <option value="best">Best Quality (320kbps)</option>
            <option value="320">High (320kbps)</option>
            <option value="256">Medium-High (256kbps)</option>
            <option value="192">Medium (192kbps)</option>
            <option value="128">Standard (128kbps)</option>
            <option value="96">Low (96kbps)</option>
        `;
        qualitySelect.value = 'best';

        // Audio format options
        formatSelect.innerHTML = `
            <option value="mp3">MP3 (Most Compatible)</option>
            <option value="m4a">M4A/AAC (Best Quality)</option>
            <option value="opus">Opus (Smallest Size)</option>
            <option value="flac">FLAC (Lossless)</option>
        `;
        // Try to restore format if it was an audio format
        if (['mp3', 'm4a', 'opus', 'flac'].includes(currentFormatValue)) {
            formatSelect.value = currentFormatValue;
        } else {
            formatSelect.value = 'mp3';
        }
    } else {
        // Video quality options (resolution-based)
        qualitySelect.innerHTML = `
            <option value="best">Best Quality</option>
            <option value="2160p">4K (2160p)</option>
            <option value="1440p">2K (1440p)</option>
            <option value="1080p">1080p (Full HD)</option>
            <option value="720p">720p (HD)</option>
            <option value="480p">480p</option>
            <option value="360p">360p</option>
            <option value="worst">Lowest Quality</option>
        `;
        // Try to restore previous value if it was a video quality
        if (['best', '2160p', '1440p', '1080p', '720p', '480p', '360p', 'worst'].includes(currentQualityValue)) {
            qualitySelect.value = currentQualityValue;
        } else {
            qualitySelect.value = 'best';
        }

        // Video format options
        formatSelect.innerHTML = `
            <option value="mp4">MP4 (Most Compatible)</option>
            <option value="webm">WebM (Smaller Size)</option>
            <option value="mkv">MKV (Best Quality)</option>
        `;
        // Try to restore format if it was a video format
        if (['mp4', 'webm', 'mkv'].includes(currentFormatValue)) {
            formatSelect.value = currentFormatValue;
        } else {
            formatSelect.value = 'mp4';
        }
    }
}

// Timeline Functions
function initializeTimeline(durationSeconds) {
    videoDurationSeconds = durationSeconds;

    // Reset handles to full range
    handleStart.style.left = '0%';
    handleEnd.style.left = '100%';

    // Update display
    timelineTotalDuration.textContent = formatTime(durationSeconds);
    updateTimelineDisplay();

    // Generate time labels below timeline
    generateTimeLabels(durationSeconds);

    // Load video thumbnails if available
    loadVideoThumbnails();
}

function generateTimeLabels(durationSeconds) {
    const labelsContainer = document.getElementById('timelineTimeLabels');
    labelsContainer.innerHTML = '';

    // Create start label
    const startLabel = document.createElement('span');
    startLabel.textContent = '0:00';
    labelsContainer.appendChild(startLabel);

    // Create middle labels
    const numLabels = Math.min(3, Math.floor(durationSeconds / 60)); // Show up to 3 middle labels
    for (let i = 1; i <= numLabels; i++) {
        const timeSeconds = (durationSeconds * i) / (numLabels + 1);
        const label = document.createElement('span');
        label.textContent = formatTime(timeSeconds);
        labelsContainer.appendChild(label);
    }

    // Create end label
    const endLabel = document.createElement('span');
    endLabel.textContent = formatTime(durationSeconds);
    labelsContainer.appendChild(endLabel);
}

function loadVideoThumbnails() {
    const thumbnailsContainer = document.getElementById('timelineThumbnails');
    const videoId = currentVideoInfo ? currentVideoInfo.id : null;

    if (!videoId) return;

    // Create a thumbnail strip using YouTube's maxresdefault
    const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
    thumbnailsContainer.style.backgroundImage = `url(${thumbnailUrl})`;
    thumbnailsContainer.style.backgroundSize = 'cover';
    thumbnailsContainer.style.backgroundPosition = 'center';
    thumbnailsContainer.style.opacity = '0.4';

    // Preload frame preview thumbnails
    preloadFramePreviews(videoId, thumbnailUrl);
}

function preloadFramePreviews(videoId, thumbnailUrl) {
    const framePreviewImgStart = document.getElementById('framePreviewImgStart');
    const framePreviewImgEnd = document.getElementById('framePreviewImgEnd');

    if (framePreviewImgStart) {
        framePreviewImgStart.src = thumbnailUrl;
        framePreviewImgStart.onerror = function() {
            this.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        };
    }

    if (framePreviewImgEnd) {
        framePreviewImgEnd.src = thumbnailUrl;
        framePreviewImgEnd.onerror = function() {
            this.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        };
    }

    // Initialize preview times
    const framePreviewTimeStart = document.getElementById('framePreviewTimeStart');
    const framePreviewTimeEnd = document.getElementById('framePreviewTimeEnd');

    if (framePreviewTimeStart) {
        framePreviewTimeStart.textContent = '0:00';
    }

    if (framePreviewTimeEnd && videoDurationSeconds) {
        framePreviewTimeEnd.textContent = formatTime(videoDurationSeconds);
    }
}

function startDragging(e, target) {
    // Don't call preventDefault here - it's already called in the event listener
    console.log('startDragging called:', target, 'isDragging:', isDragging);
    isDragging = true;
    dragTarget = target;
    document.body.style.cursor = 'grabbing';

    // Add dragging class for frame preview
    if (target === 'start') {
        handleStart.classList.add('dragging');
    } else {
        handleEnd.classList.add('dragging');
    }
    console.log('Dragging started. isDragging:', isDragging, 'dragTarget:', dragTarget);
}

function stopDragging() {
    if (isDragging) {
        isDragging = false;
        dragTarget = null;
        document.body.style.cursor = '';

        // Remove dragging class
        handleStart.classList.remove('dragging');
        handleEnd.classList.remove('dragging');

        // Auto-update preview if it's open
        autoUpdatePreview();
    }
}

function autoUpdatePreview() {
    // Only update if preview is visible and player is ready
    if (!videoPreviewContainer.classList.contains('hidden') && youtubePlayer && playerReady) {
        // Get current trim times
        const startPercent = parseFloat(handleStart.style.left) || 0;
        const endPercent = parseFloat(handleEnd.style.left) || 100;

        previewStartTime = Math.floor((startPercent / 100) * videoDurationSeconds);
        previewEndTime = Math.floor((endPercent / 100) * videoDurationSeconds);

        console.log('Auto-updating preview to:', previewStartTime, '-', previewEndTime);

        // Add visual feedback
        showPreviewUpdateFlash();

        // Seek to new start time and play
        youtubePlayer.seekTo(previewStartTime, true);
        youtubePlayer.playVideo();
    }
}

function showPreviewUpdateFlash() {
    const playerWrapper = document.querySelector('.video-player-wrapper');
    if (!playerWrapper) return;

    // Add flash effect
    playerWrapper.style.boxShadow = '0 0 20px rgba(62, 166, 255, 0.8)';
    playerWrapper.style.transition = 'box-shadow 0.3s ease';

    setTimeout(() => {
        playerWrapper.style.boxShadow = '';
    }, 300);
}

function onDrag(e) {
    if (!isDragging || !dragTarget) return;

    // Don't call preventDefault here - it's already called in the event listener

    const rect = timelineTrack.getBoundingClientRect();
    // For touch events, clientX is directly on the touch object
    // For mouse events, it's on the event object
    const x = (e.clientX !== undefined ? e.clientX : e.pageX) - rect.left;
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));

    // Get current positions
    const startPercent = parseFloat(handleStart.style.left);
    const endPercent = parseFloat(handleEnd.style.left);

    // Update position based on which handle is being dragged
    if (dragTarget === 'start') {
        // Ensure start doesn't go past end
        if (percent < endPercent - 1) {
            handleStart.style.left = percent + '%';
            updateFramePreview('start', percent);
        }
    } else if (dragTarget === 'end') {
        // Ensure end doesn't go before start
        if (percent > startPercent + 1) {
            handleEnd.style.left = percent + '%';
            updateFramePreview('end', percent);
        }
    }

    updateTimelineDisplay();
}

function updateFramePreview(handle, percent) {
    const timeSeconds = (percent / 100) * videoDurationSeconds;
    const videoId = currentVideoInfo ? currentVideoInfo.id : null;

    if (!videoId) return;

    // Update time display
    const timeElement = document.getElementById(`framePreviewTime${handle === 'start' ? 'Start' : 'End'}`);

    if (timeElement) {
        timeElement.textContent = formatTime(timeSeconds);
    }

    // Note: We're using the video thumbnail which doesn't change based on timestamp
    // For a true "scrubbing" effect with different frames, we would need:
    // 1. YouTube's storyboard API (not publicly available)
    // 2. Or server-side video processing to extract frames
    // The current implementation shows the video thumbnail with the timestamp
}

function updateTimelineDisplay() {
    const startPercent = parseFloat(handleStart.style.left);
    const endPercent = parseFloat(handleEnd.style.left);

    // Calculate times in seconds
    const startSeconds = (startPercent / 100) * videoDurationSeconds;
    const endSeconds = (endPercent / 100) * videoDurationSeconds;
    const durationSeconds = endSeconds - startSeconds;

    // Update visual selection region
    const selectedRegion = timelineSelection.querySelector('.timeline-selected-region');
    selectedRegion.style.left = startPercent + '%';
    selectedRegion.style.width = (endPercent - startPercent) + '%';

    // Update dark overlays
    const overlayLeft = document.getElementById('overlayLeft');
    const overlayRight = document.getElementById('overlayRight');
    overlayLeft.style.width = startPercent + '%';
    overlayRight.style.width = (100 - endPercent) + '%';

    // Update tooltips
    tooltipStart.textContent = formatTime(startSeconds);
    tooltipEnd.textContent = formatTime(endSeconds);

    // Update info display
    if (startPercent === 0 && endPercent === 100) {
        selectedDuration.textContent = 'Full Video';
        trimmingRange.textContent = 'Drag handles to trim';

        // Clear manual inputs
        startTimeInput.value = '';
        endTimeInput.value = '';
    } else {
        selectedDuration.textContent = formatTime(durationSeconds);
        trimmingRange.textContent = `${formatTime(startSeconds)} → ${formatTime(endSeconds)}`;

        // Update manual inputs
        startTimeInput.value = formatTimeHHMMSS(startSeconds);
        endTimeInput.value = formatTimeHHMMSS(endSeconds);
    }
}

function syncTimelineFromInputs() {
    const startTime = startTimeInput.value.trim();
    const endTime = endTimeInput.value.trim();

    if (!videoDurationSeconds) return;

    if (startTime) {
        const startSeconds = parseTimeToSeconds(startTime);
        if (startSeconds >= 0 && startSeconds < videoDurationSeconds) {
            const startPercent = (startSeconds / videoDurationSeconds) * 100;
            handleStart.style.left = startPercent + '%';
        }
    }

    if (endTime) {
        const endSeconds = parseTimeToSeconds(endTime);
        if (endSeconds > 0 && endSeconds <= videoDurationSeconds) {
            const endPercent = (endSeconds / videoDurationSeconds) * 100;
            handleEnd.style.left = endPercent + '%';
        }
    }

    updateTimelineDisplay();

    // Auto-update preview if it's open
    autoUpdatePreview();
}

function parseTimeToSeconds(timeString) {
    const parts = timeString.split(':').map(p => parseInt(p) || 0);

    if (parts.length === 3) {
        return parts[0] * 3600 + parts[1] * 60 + parts[2];
    } else if (parts.length === 2) {
        return parts[0] * 60 + parts[1];
    } else if (parts.length === 1) {
        return parts[0];
    }

    return 0;
}

function formatTime(seconds) {
    seconds = Math.floor(seconds);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
}

function formatTimeHHMMSS(seconds) {
    seconds = Math.floor(seconds);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// Functions
async function fetchVideoInfo() {
    const url = videoUrl.value.trim();

    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }

    if (!isValidYouTubeUrl(url)) {
        showError('Please enter a valid YouTube URL');
        return;
    }

    // Show loading state
    fetchInfoBtn.disabled = true;
    fetchInfoBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" class="loading">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-dasharray="32" stroke-dashoffset="32"/>
        </svg>
        Loading...
    `;

    try {
        const response = await fetch('/api/video-info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch video info');
        }

        currentVideoInfo = data;
        displayVideoInfo(data);
        showSection('options');

    } catch (error) {
        showError(error.message);
    } finally {
        fetchInfoBtn.disabled = false;
        fetchInfoBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Fetch Info
        `;
    }
}

function displayVideoInfo(info) {
    videoThumbnail.src = info.thumbnail;
    videoTitle.textContent = info.title;
    videoUploader.textContent = `👤 ${info.uploader}`;
    videoDuration.textContent = `⏱️ ${info.duration}`;
    videoInfoSection.classList.remove('hidden');

    // Initialize the timeline trimmer with video duration
    if (info.duration_seconds) {
        initializeTimeline(info.duration_seconds);
    }
}

async function startDownload() {
    console.log('Download button clicked!');
    const url = videoUrl.value.trim();
    const quality = qualitySelect.value;
    const format = formatSelect.value;
    const startTime = startTimeInput.value.trim();
    const endTime = endTimeInput.value.trim();

    console.log('Download params:', { url, quality, format, formatType: selectedFormatType, startTime, endTime });
    console.log('Socket ID:', socket.id);

    // Validate time format if provided
    if (startTime && !isValidTimeFormat(startTime)) {
        console.error('Invalid start time format');
        showError('Invalid start time format. Use HH:MM:SS');
        return;
    }

    if (endTime && !isValidTimeFormat(endTime)) {
        console.error('Invalid end time format');
        showError('Invalid end time format. Use HH:MM:SS');
        return;
    }

    console.log('Showing progress section...');
    // Show progress section
    showSection('progress');
    resetProgress();

    downloadBtn.disabled = true;

    try {
        console.log('Sending download request to server...');
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                quality,
                format: format,
                format_type: selectedFormatType,
                start_time: startTime || null,
                end_time: endTime || null,
                socket_id: socket.id,
            }),
        });

        console.log('Response received:', response.status);
        const data = await response.json();
        console.log('Response data:', data);

        if (!response.ok) {
            throw new Error(data.error || 'Download failed');
        }

        currentDownloadId = data.download_id;
        progressStatus.textContent = 'Starting download...';
        console.log('Download started with ID:', currentDownloadId);

        // Start fallback polling in case socket connection drops
        startPollingDownloadStatus();

    } catch (error) {
        console.error('Download error:', error);
        showError(error.message);
        downloadBtn.disabled = false;
    }
}

function resetProgress() {
    progressBarFill.style.width = '0%';
    progressPercent.textContent = '0%';
    progressSpeed.textContent = 'Speed: --';
    progressEta.textContent = 'ETA: --';
    progressStatus.textContent = 'Initializing...';
}

function showSection(section) {
    // Hide all sections
    videoInfoSection.classList.add('hidden');
    downloadOptionsSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    completeSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    // Show requested section
    switch (section) {
        case 'options':
            videoInfoSection.classList.remove('hidden');
            downloadOptionsSection.classList.remove('hidden');
            break;
        case 'progress':
            videoInfoSection.classList.remove('hidden');
            progressSection.classList.remove('hidden');
            break;
        case 'complete':
            completeSection.classList.remove('hidden');
            break;
        case 'error':
            errorSection.classList.remove('hidden');
            break;
    }
}

function showError(message) {
    errorMessage.textContent = message;
    showSection('error');
}

function reset() {
    // Clear inputs
    videoUrl.value = '';
    startTimeInput.value = '';
    endTimeInput.value = '';
    qualitySelect.value = 'best';
    formatSelect.value = 'mp4';

    // Reset format type
    formatTypeButtons.forEach(btn => btn.classList.remove('active'));
    formatTypeButtons[0].classList.add('active');
    selectedFormatType = 'video';

    // Update options to video defaults
    updateQualityOptions('video');

    // Reset state
    currentDownloadId = null;
    currentVideoInfo = null;
    videoDurationSeconds = 0;
    lastProgressUpdate = null;

    // Stop any active polling
    stopPollingDownloadStatus();

    // Reset timeline
    handleStart.style.left = '0%';
    handleEnd.style.left = '100%';
    manualTimeInputs.classList.add('hidden');

    // Enable download button
    downloadBtn.disabled = false;

    // Close preview and cleanup
    if (!videoPreviewContainer.classList.contains('hidden')) {
        closePreview();
    }
    if (youtubePlayer) {
        youtubePlayer.destroy();
        youtubePlayer = null;
        playerReady = false;
    }

    // Hide all sections except URL input
    videoInfoSection.classList.add('hidden');
    downloadOptionsSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    completeSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    // Focus URL input
    videoUrl.focus();
}

function isValidYouTubeUrl(url) {
    const patterns = [
        /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/,
        /^(https?:\/\/)?(www\.)?youtube\.com\/shorts\/[\w-]+/,  // YouTube Shorts
        /^(https?:\/\/)?(www\.)?youtube\.com\/playlist\?list=[\w-]+/
    ];
    return patterns.some(pattern => pattern.test(url));
}

function isValidTimeFormat(time) {
    // Check HH:MM:SS format
    const pattern = /^([0-9]{1,2}):([0-5][0-9]):([0-5][0-9])$/;
    return pattern.test(time);
}

// Format time input on blur
[startTimeInput, endTimeInput].forEach(input => {
    input.addEventListener('blur', (e) => {
        const value = e.target.value.trim();
        if (value && !value.includes(':')) {
            // If only numbers, treat as seconds and convert to HH:MM:SS
            const totalSeconds = parseInt(value);
            if (!isNaN(totalSeconds)) {
                const hours = Math.floor(totalSeconds / 3600);
                const minutes = Math.floor((totalSeconds % 3600) / 60);
                const seconds = totalSeconds % 60;
                e.target.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }
        }
    });
});

// YouTube Player Preview
let youtubePlayer = null;
let playerReady = false;
let previewStartTime = 0;
let previewEndTime = 0;
let previewInterval = null;
let youtubeAPIReady = false;

const previewBtn = document.getElementById('previewBtn');
const closePreviewBtn = document.getElementById('closePreviewBtn');
const replayPreviewBtn = document.getElementById('replayPreviewBtn');
const videoPreviewContainer = document.getElementById('videoPreviewContainer');
const setStartPointBtn = document.getElementById('setStartPointBtn');
const setEndPointBtn = document.getElementById('setEndPointBtn');
const currentPlaybackTime = document.getElementById('currentPlaybackTime');
const playbackTimeOverlay = document.getElementById('playbackTimeOverlay');

// Track playback time
let playbackTimeInterval = null;

// YouTube IFrame API callback
window.onYouTubeIframeAPIReady = function() {
    console.log('YouTube IFrame API ready');
    youtubeAPIReady = true;
};

function initializeYouTubePlayer(videoId) {
    console.log('Initializing YouTube player with video ID:', videoId);

    if (youtubePlayer) {
        console.log('Destroying existing player');
        youtubePlayer.destroy();
        youtubePlayer = null;
        playerReady = false;
    }

    // Make sure the container exists and is visible
    const playerElement = document.getElementById('youtubePlayer');
    if (!playerElement) {
        console.error('YouTube player element not found!');
        return;
    }

    try {
        youtubePlayer = new YT.Player('youtubePlayer', {
            height: '360',
            width: '640',
            videoId: videoId,
            playerVars: {
                'playsinline': 1,
                'rel': 0,
                'modestbranding': 1,
                'controls': 1,
                'enablejsapi': 1
            },
            events: {
                'onReady': onPlayerReady,
                'onStateChange': onPlayerStateChange,
                'onError': onPlayerError
            }
        });
        console.log('YouTube player created');
    } catch (error) {
        console.error('Error creating YouTube player:', error);
    }
}

function onPlayerError(event) {
    console.error('YouTube player error:', event.data);
    const errorMessages = {
        2: 'Invalid video ID',
        5: 'HTML5 player error',
        100: 'Video not found or private',
        101: 'Video not allowed to be played in embedded players',
        150: 'Video not allowed to be played in embedded players'
    };
    alert('YouTube Player Error: ' + (errorMessages[event.data] || 'Unknown error'));
}

function onPlayerReady(event) {
    playerReady = true;
    console.log('Player ready event fired, playerReady set to:', playerReady);
    console.log('Player object:', youtubePlayer);
}

function onPlayerStateChange(event) {
    // Monitor playback and stop at end time
    if (event.data === YT.PlayerState.PLAYING) {
        // Start tracking playback time
        startPlaybackTimeTracking();

        if (previewInterval) {
            clearInterval(previewInterval);
        }

        previewInterval = setInterval(() => {
            const currentTime = youtubePlayer.getCurrentTime();
            if (currentTime >= previewEndTime) {
                youtubePlayer.pauseVideo();
                clearInterval(previewInterval);
                previewInterval = null;
            }
        }, 100);
    } else if (event.data === YT.PlayerState.PAUSED || event.data === YT.PlayerState.ENDED) {
        if (previewInterval) {
            clearInterval(previewInterval);
            previewInterval = null;
        }
        // Continue tracking time even when paused so user can set trim points
    }
}

function getVideoIdFromUrl(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})(?:[?&]|$)/,
        /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})(?:[?&]|$)/,  // YouTube Shorts
        /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})(?:[?&]|$)/
    ];

    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match && match[1]) {
            return match[1];
        }
    }
    return null;
}

function showPreview() {
    const url = videoUrl.value.trim();
    const videoId = getVideoIdFromUrl(url);

    console.log('Show preview called for:', url);
    console.log('Extracted video ID:', videoId);

    if (!videoId) {
        alert('Cannot extract video ID from URL');
        return;
    }

    // Get current trim times
    const startPercent = parseFloat(handleStart.style.left) || 0;
    const endPercent = parseFloat(handleEnd.style.left) || 100;

    previewStartTime = Math.floor((startPercent / 100) * videoDurationSeconds);
    previewEndTime = Math.floor((endPercent / 100) * videoDurationSeconds);

    console.log('Preview times:', previewStartTime, 'to', previewEndTime);

    // Show preview container
    videoPreviewContainer.classList.remove('hidden');

    // Check if YouTube API is ready
    if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
        console.log('YouTube API not ready, waiting...');
        const waitForAPI = setInterval(() => {
            if (typeof YT !== 'undefined' && typeof YT.Player !== 'undefined') {
                console.log('YouTube API now ready');
                clearInterval(waitForAPI);
                createPlayerAndPlay(videoId);
            }
        }, 100);
        return;
    }

    createPlayerAndPlay(videoId);
}

function createPlayerAndPlay(videoId) {
    // Initialize player if not exists
    if (!youtubePlayer) {
        console.log('Creating new player');
        initializeYouTubePlayer(videoId);

        // Wait for player to be ready, then play
        let attempts = 0;
        const checkReady = setInterval(() => {
            attempts++;
            if (playerReady) {
                console.log('Player ready, starting playback');
                clearInterval(checkReady);
                playPreview();
            } else if (attempts > 50) {
                clearInterval(checkReady);
                console.error('Player failed to initialize after 5 seconds');
                alert('Failed to initialize video player. Please try again.');
            }
        }, 100);
    } else {
        console.log('Using existing player');
        // Load new video if different
        try {
            const currentVideoData = youtubePlayer.getVideoData();
            if (currentVideoData.video_id !== videoId) {
                console.log('Loading different video:', videoId);
                playerReady = false;
                youtubePlayer.loadVideoById(videoId);
                let attempts = 0;
                const checkReady = setInterval(() => {
                    attempts++;
                    if (playerReady) {
                        console.log('New video loaded and ready');
                        clearInterval(checkReady);
                        playPreview();
                    } else if (attempts > 50) {
                        clearInterval(checkReady);
                        console.error('Failed to load new video');
                    }
                }, 100);
            } else {
                console.log('Same video, just playing');
                playPreview();
            }
        } catch (error) {
            console.error('Error checking video data:', error);
            playPreview();
        }
    }
}

function playPreview() {
    console.log('playPreview called, playerReady:', playerReady);
    if (youtubePlayer && playerReady) {
        console.log('Seeking to', previewStartTime, 'and playing');
        youtubePlayer.seekTo(previewStartTime, true);
        youtubePlayer.playVideo();

        // Start tracking playback time
        startPlaybackTimeTracking();
    } else {
        console.error('Cannot play: player not ready or not initialized');
    }
}

function closePreview() {
    videoPreviewContainer.classList.add('hidden');
    if (youtubePlayer) {
        youtubePlayer.pauseVideo();
    }
    if (previewInterval) {
        clearInterval(previewInterval);
        previewInterval = null;
    }
    stopPlaybackTimeTracking();
}

function startPlaybackTimeTracking() {
    if (playbackTimeInterval) {
        clearInterval(playbackTimeInterval);
    }

    playbackTimeInterval = setInterval(() => {
        if (youtubePlayer && playerReady) {
            try {
                const currentTime = youtubePlayer.getCurrentTime();
                const timeString = formatTime(currentTime);

                if (currentPlaybackTime) {
                    currentPlaybackTime.textContent = timeString;
                }

                if (playbackTimeOverlay) {
                    playbackTimeOverlay.textContent = timeString;
                }
            } catch (error) {
                console.error('Error getting current time:', error);
            }
        }
    }, 100); // Update every 100ms for smooth display
}

function stopPlaybackTimeTracking() {
    if (playbackTimeInterval) {
        clearInterval(playbackTimeInterval);
        playbackTimeInterval = null;
    }
}

function setTrimStartPoint() {
    if (!youtubePlayer || !playerReady) {
        alert('Please wait for the video player to be ready');
        return;
    }

    try {
        const currentTime = youtubePlayer.getCurrentTime();
        const percent = (currentTime / videoDurationSeconds) * 100;

        // Make sure it doesn't go past the end handle
        const endPercent = parseFloat(handleEnd.style.left) || 100;

        if (percent < endPercent - 1) {
            handleStart.style.left = percent + '%';
            updateTimelineDisplay();

            // Show visual feedback
            showTrimPointSetFeedback(setStartPointBtn, 'Start');

            console.log('Start point set to:', currentTime, 'seconds');
        } else {
            alert('Start point must be before the end point');
        }
    } catch (error) {
        console.error('Error setting start point:', error);
        alert('Failed to set start point');
    }
}

function setTrimEndPoint() {
    if (!youtubePlayer || !playerReady) {
        alert('Please wait for the video player to be ready');
        return;
    }

    try {
        const currentTime = youtubePlayer.getCurrentTime();
        const percent = (currentTime / videoDurationSeconds) * 100;

        // Make sure it doesn't go before the start handle
        const startPercent = parseFloat(handleStart.style.left) || 0;

        if (percent > startPercent + 1) {
            handleEnd.style.left = percent + '%';
            updateTimelineDisplay();

            // Show visual feedback
            showTrimPointSetFeedback(setEndPointBtn, 'End');

            console.log('End point set to:', currentTime, 'seconds');
        } else {
            alert('End point must be after the start point');
        }
    } catch (error) {
        console.error('Error setting end point:', error);
        alert('Failed to set end point');
    }
}

function showTrimPointSetFeedback(button, pointType) {
    // Add success animation
    const originalText = button.innerHTML;

    button.style.background = 'linear-gradient(135deg, #00c853 0%, #00a843 100%)';
    button.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M8 12L11 15L16 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        ${pointType} Set!
    `;

    setTimeout(() => {
        button.style.background = '';
        button.innerHTML = originalText;
    }, 1000);
}

// Preview event listeners
previewBtn.addEventListener('click', showPreview);
closePreviewBtn.addEventListener('click', closePreview);
replayPreviewBtn.addEventListener('click', playPreview);
setStartPointBtn.addEventListener('click', setTrimStartPoint);
setEndPointBtn.addEventListener('click', setTrimEndPoint);

// Keyboard shortcuts for trim points
document.addEventListener('keydown', (e) => {
    // Only work when preview is open and we're not typing in an input
    if (videoPreviewContainer.classList.contains('hidden') ||
        e.target.tagName === 'INPUT' ||
        e.target.tagName === 'TEXTAREA') {
        return;
    }

    switch(e.key.toLowerCase()) {
        case 'i':
            e.preventDefault();
            setTrimStartPoint();
            break;
        case 'o':
            e.preventDefault();
            setTrimEndPoint();
            break;
        case ' ':
            e.preventDefault();
            if (youtubePlayer && playerReady) {
                const state = youtubePlayer.getPlayerState();
                if (state === YT.PlayerState.PLAYING) {
                    youtubePlayer.pauseVideo();
                } else {
                    youtubePlayer.playVideo();
                }
            }
            break;
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    videoUrl.focus();
});
