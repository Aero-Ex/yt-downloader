// Initialize Socket.IO
const socket = io();

// State management
let currentDownloadId = null;
let currentVideoInfo = null;
let selectedFormatType = 'video';
let videoDurationSeconds = 0;
let isDragging = false;
let dragTarget = null;

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
    console.log('Connected to server');
});

socket.on('download_progress', (data) => {
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
    currentDownloadId = data.download_id;
    showSection('complete');
    downloadedFileName.textContent = data.filename;
});

socket.on('download_error', (data) => {
    showError(data.error);
});

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
handleStart.addEventListener('touchstart', (e) => startDragging(e.touches[0], 'start'));
handleEnd.addEventListener('touchstart', (e) => startDragging(e.touches[0], 'end'));

document.addEventListener('touchmove', (e) => onDrag(e.touches[0]));
document.addEventListener('touchend', stopDragging);

// Manual time input sync
startTimeInput.addEventListener('input', syncTimelineFromInputs);
endTimeInput.addEventListener('input', syncTimelineFromInputs);

// Timeline Functions
function initializeTimeline(durationSeconds) {
    videoDurationSeconds = durationSeconds;

    // Reset handles to full range
    handleStart.style.left = '0%';
    handleEnd.style.left = '100%';

    // Update display
    timelineTotalDuration.textContent = formatTime(durationSeconds);
    updateTimelineDisplay();

    // Generate time markers
    generateTimeMarkers(durationSeconds);
}

function generateTimeMarkers(durationSeconds) {
    const markers = document.getElementById('timelineMarkers');
    markers.innerHTML = '';

    // Generate markers at intervals
    const numMarkers = Math.min(10, Math.floor(durationSeconds / 30));

    for (let i = 1; i < numMarkers; i++) {
        const percent = (i / numMarkers) * 100;
        const timeSeconds = (durationSeconds * i) / numMarkers;

        const marker = document.createElement('div');
        marker.className = 'timeline-marker';
        marker.style.left = percent + '%';

        const label = document.createElement('div');
        label.className = 'timeline-marker-label';
        label.textContent = formatTime(timeSeconds);
        marker.appendChild(label);

        markers.appendChild(marker);
    }
}

function startDragging(e, target) {
    e.preventDefault();
    isDragging = true;
    dragTarget = target;
    document.body.style.cursor = 'grabbing';
}

function stopDragging() {
    if (isDragging) {
        isDragging = false;
        dragTarget = null;
        document.body.style.cursor = '';
    }
}

function onDrag(e) {
    if (!isDragging || !dragTarget) return;

    e.preventDefault();

    const rect = timelineTrack.getBoundingClientRect();
    const x = (e.clientX || e.pageX) - rect.left;
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));

    // Get current positions
    const startPercent = parseFloat(handleStart.style.left);
    const endPercent = parseFloat(handleEnd.style.left);

    // Update position based on which handle is being dragged
    if (dragTarget === 'start') {
        // Ensure start doesn't go past end
        if (percent < endPercent - 1) {
            handleStart.style.left = percent + '%';
        }
    } else if (dragTarget === 'end') {
        // Ensure end doesn't go before start
        if (percent > startPercent + 1) {
            handleEnd.style.left = percent + '%';
        }
    }

    updateTimelineDisplay();
}

function updateTimelineDisplay() {
    const startPercent = parseFloat(handleStart.style.left);
    const endPercent = parseFloat(handleEnd.style.left);

    // Calculate times in seconds
    const startSeconds = (startPercent / 100) * videoDurationSeconds;
    const endSeconds = (endPercent / 100) * videoDurationSeconds;
    const durationSeconds = endSeconds - startSeconds;

    // Update visual selection
    const selectedRegion = timelineSelection.querySelector('.timeline-selected-region');
    selectedRegion.style.left = startPercent + '%';
    selectedRegion.style.width = (endPercent - startPercent) + '%';

    // Update tooltips
    tooltipStart.textContent = formatTime(startSeconds);
    tooltipEnd.textContent = formatTime(endSeconds);

    // Update info display
    if (startPercent === 0 && endPercent === 100) {
        selectedDuration.textContent = 'Full Video';
        trimmingRange.textContent = 'None';

        // Clear manual inputs
        startTimeInput.value = '';
        endTimeInput.value = '';
    } else {
        selectedDuration.textContent = formatTime(durationSeconds);
        trimmingRange.textContent = `${formatTime(startSeconds)} - ${formatTime(endSeconds)}`;

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
    const url = videoUrl.value.trim();
    const quality = qualitySelect.value;
    const startTime = startTimeInput.value.trim();
    const endTime = endTimeInput.value.trim();

    // Validate time format if provided
    if (startTime && !isValidTimeFormat(startTime)) {
        showError('Invalid start time format. Use HH:MM:SS');
        return;
    }

    if (endTime && !isValidTimeFormat(endTime)) {
        showError('Invalid end time format. Use HH:MM:SS');
        return;
    }

    // Show progress section
    showSection('progress');
    resetProgress();

    downloadBtn.disabled = true;

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                quality,
                format_type: selectedFormatType,
                start_time: startTime || null,
                end_time: endTime || null,
                socket_id: socket.id,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Download failed');
        }

        currentDownloadId = data.download_id;
        progressStatus.textContent = 'Starting download...';

    } catch (error) {
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

    // Reset format type
    formatTypeButtons.forEach(btn => btn.classList.remove('active'));
    formatTypeButtons[0].classList.add('active');
    selectedFormatType = 'video';

    // Reset state
    currentDownloadId = null;
    currentVideoInfo = null;
    videoDurationSeconds = 0;

    // Reset timeline
    handleStart.style.left = '0%';
    handleEnd.style.left = '100%';
    manualTimeInputs.classList.add('hidden');

    // Enable download button
    downloadBtn.disabled = false;

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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    videoUrl.focus();
});
