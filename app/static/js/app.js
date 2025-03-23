// Constants
const UPDATE_INTERVAL = 1000; // Update song info every 1 second

// State
let currentStatus = 'stopped';
let currentSongInfo = null;
let currentPlaylistSongs = [];
let currentPlaylistId = null;
let allPlaylists = [];
let seeking = false;
let updatingVolume = false;
let currentDirectory = null;

// DOM Elements - Main Controls
const playPauseBtn = document.getElementById('play-pause-btn');
const playPauseIcon = document.getElementById('play-pause-icon');
const previousBtn = document.getElementById('previous-btn');
const nextBtn = document.getElementById('next-btn');
const volumeSlider = document.getElementById('volume-slider');
const volumeLevel = document.getElementById('volume-level');

// DOM Elements - Song Info
const noSongPlaying = document.getElementById('no-song-playing');
const currentSongInfoElement = document.getElementById('current-song-info');
const songTitle = document.getElementById('song-title');
const songArtist = document.getElementById('song-artist');
const songAlbum = document.getElementById('song-album');
const currentTime = document.getElementById('current-time');
const totalTime = document.getElementById('total-time');
const progressBar = document.getElementById('progress-bar');
const seekSlider = document.getElementById('seek-slider');

// DOM Elements - Playlists
const playlistList = document.getElementById('playlist-list');
const mobilePlaylistList = document.getElementById('mobile-playlist-list');
const nowPlayingList = document.getElementById('now-playing-list');
const newPlaylistBtn = document.getElementById('new-playlist-btn');
const renamePlaylistBtn = document.getElementById('rename-playlist-btn');
const deletePlaylistBtn = document.getElementById('delete-playlist-btn');

// DOM Elements - File Browser
const fileBrowser = document.getElementById('file-browser');
const mobileFileBrowser = document.getElementById('mobile-file-browser');

// DOM Elements - Settings
const settingsModal = document.getElementById('settings-modal');
const openSettings = document.getElementById('open-settings');
const desktopOpenSettings = document.getElementById('desktop-open-settings');
const closeSettings = document.getElementById('close-settings');
const toggleRepeat = document.getElementById('toggle-repeat');
const repeatIndicator = document.getElementById('repeat-indicator');
const toggleShuffle = document.getElementById('toggle-shuffle');
const shuffleIndicator = document.getElementById('shuffle-indicator');
const toggleStopAfter = document.getElementById('toggle-stop-after');
const stopAfterIndicator = document.getElementById('stop-after-indicator');
const toggleAutoAdvance = document.getElementById('toggle-auto-advance');
const autoAdvanceIndicator = document.getElementById('auto-advance-indicator');

// DOM Elements - Mobile
const mobileSidebar = document.getElementById('mobile-sidebar');
const openSidebar = document.getElementById('open-sidebar');
const closeSidebar = document.getElementById('close-sidebar');

// DOM Elements - Dialog
const inputDialog = document.getElementById('input-dialog');
const dialogTitle = document.getElementById('dialog-title');
const dialogInput = document.getElementById('dialog-input');
const dialogCancel = document.getElementById('dialog-cancel');
const dialogConfirm = document.getElementById('dialog-confirm');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners
    setupEventListeners();
    
    // Initial data load
    loadInitialData();
    
    // Start update interval
    setInterval(updatePlayerStatus, UPDATE_INTERVAL);
});

// Set up event listeners for all interactive elements
function setupEventListeners() {
    // Player Controls
    playPauseBtn.addEventListener('click', togglePlayPause);
    previousBtn.addEventListener('click', playPrevious);
    nextBtn.addEventListener('click', playNext);
    
    // Volume Controls
    volumeSlider.addEventListener('input', handleVolumeChange);
    volumeSlider.addEventListener('change', () => {
        updatingVolume = false;
    });
    volumeSlider.addEventListener('mousedown', () => {
        updatingVolume = true;
    });
    volumeSlider.addEventListener('touchstart', () => {
        updatingVolume = true;
    });
    
    // Seek Controls
    seekSlider.addEventListener('input', handleSeek);
    seekSlider.addEventListener('change', () => {
        seeking = false;
    });
    seekSlider.addEventListener('mousedown', () => {
        seeking = true;
    });
    seekSlider.addEventListener('touchstart', () => {
        seeking = true;
    });
    
    // Playlist Controls
    newPlaylistBtn.addEventListener('click', handleNewPlaylist);
    renamePlaylistBtn.addEventListener('click', handleRenamePlaylist);
    deletePlaylistBtn.addEventListener('click', handleDeletePlaylist);
    
    // Settings Controls
    openSettings.addEventListener('click', showSettings);
    desktopOpenSettings.addEventListener('click', showSettings);
    closeSettings.addEventListener('click', hideSettings);
    toggleRepeat.addEventListener('click', handleToggleRepeat);
    toggleShuffle.addEventListener('click', handleToggleShuffle);
    toggleStopAfter.addEventListener('click', handleToggleStopAfter);
    toggleAutoAdvance.addEventListener('click', handleToggleAutoAdvance);
    
    // Mobile Controls
    openSidebar.addEventListener('click', showSidebar);
    closeSidebar.addEventListener('click', hideSidebar);
    
    // Dialog Controls
    dialogCancel.addEventListener('click', hideDialog);
    dialogConfirm.addEventListener('click', handleDialogConfirm);
    
    // Close modals when clicking outside
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            hideSettings();
        }
    });
    
    inputDialog.addEventListener('click', (e) => {
        if (e.target === inputDialog) {
            hideDialog();
        }
    });
}

// Load initial data from the server
function loadInitialData() {
    Promise.all([
        fetchStatus(),
        fetchPlaylists(),
        fetchCurrentPlaylist(),
        fetchFileBrowser()
    ]).then(() => {
        // Initial UI update
        updateUI();
    }).catch(error => {
        console.error('Error loading initial data:', error);
    });
}

// API Calls

// Fetch the current player status
function fetchStatus() {
    return fetch('/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentStatus = data.status;
                currentSongInfo = data.current_song;
                updateSettingsUI(data.settings);
                updateVolumeUI(data.volume);
            }
        });
}

// Fetch all playlists
function fetchPlaylists() {
    return fetch('/playlists/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allPlaylists = data.playlists;
                currentPlaylistId = data.current_playlist;
                updatePlaylistsUI();
            }
        });
}

// Fetch the current playlist
function fetchCurrentPlaylist() {
    return fetch('/playlists/current')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentPlaylistSongs = data.songs;
                updateNowPlayingUI(data.current_position);
            }
        });
}

// Fetch file browser contents
function fetchFileBrowser(directory = null) {
    let url = '/files/browse';
    if (directory) {
        url += `?directory=${encodeURIComponent(directory)}`;
    }
    
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentDirectory = data.directory;
                updateFileBrowserUI();
            }
        });
}

// Player Controls

// Toggle play/pause
function togglePlayPause() {
    fetch('/player/playpause', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => {
        // Update will happen in the next interval
    });
}

// Play the previous song
function playPrevious() {
    fetch('/player/previous', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => {
        // Update will happen in the next interval
    });
}

// Play the next song
function playNext() {
    fetch('/player/next', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => {
        // Update will happen in the next interval
    });
}

// Handle volume change
function handleVolumeChange() {
    const volume = volumeSlider.value;
    
    // Update UI immediately
    volumeLevel.style.width = `${volume}%`;
    
    // Send to server
    fetch('/player/volume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ volume })
    });
}

// Handle seeking
function handleSeek() {
    const position = seekSlider.value;
    const totalSeconds = currentSongInfo.length_seconds;
    const seekPosition = Math.floor((position * totalSeconds) / 100);
    
    // Update UI immediately
    progressBar.style.width = `${position}%`;
    currentTime.textContent = formatTime(seekPosition);
    
    // Send to server
    fetch('/player/seek', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position: seekPosition })
    });
}

// Playlist Management

// Handle creating a new playlist
function handleNewPlaylist() {
    showDialog('Create New Playlist', '', (name) => {
        fetch('/playlists/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        })
        .then(() => fetchPlaylists());
    });
}

// Handle renaming the current playlist
function handleRenamePlaylist() {
    const currentPlaylist = allPlaylists.find(p => p.is_current);
    if (!currentPlaylist) return;
    
    showDialog('Rename Playlist', currentPlaylist.name, (name) => {
        fetch('/playlists/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        })
        .then(() => fetchPlaylists());
    });
}

// Handle deleting the current playlist
function handleDeletePlaylist() {
    if (confirm('Are you sure you want to delete this playlist?')) {
        fetch('/playlists/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(() => fetchPlaylists());
    }
}

// Handle selecting a playlist
function selectPlaylist(id) {
    fetch(`/playlists/set-current/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => {
        fetchPlaylists();
        fetchCurrentPlaylist();
    });
}

// Settings Management

// Toggle repeat setting
function handleToggleRepeat() {
    fetch('/player/settings/toggle-repeat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => fetchStatus());
}

// Toggle shuffle setting
function handleToggleShuffle() {
    fetch('/player/settings/toggle-shuffle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => fetchStatus());
}

// Toggle stop after current song setting
function handleToggleStopAfter() {
    fetch('/player/settings/toggle-stop-after', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => fetchStatus());
}

// Toggle auto advance setting
function handleToggleAutoAdvance() {
    fetch('/player/settings/toggle-auto-advance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => fetchStatus());
}

// File Browser Management

// Navigate to a directory
function navigateToDirectory(path) {
    fetchFileBrowser(path);
}

// Play a file
function playFile(path) {
    fetch('/files/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
    })
    .then(() => {
        // Update will happen in the next interval
        hideSidebar();
    });
}

// Add a file to the playlist
function addFileToPlaylist(path) {
    fetch('/files/add-to-playlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
    })
    .then(() => {
        fetchCurrentPlaylist();
        alert('Added to playlist');
    });
}

// Play a song from the playlist
function playPlaylistSong(position) {
    fetch(`/playlists/jump/${position}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(() => {
        fetch('/player/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
    })
    .then(() => {
        // Update will happen in the next interval
    });
}

// Delete a song from the playlist
function deletePlaylistSong(position, event) {
    event.stopPropagation();
    if (confirm('Remove this song from the playlist?')) {
        fetch(`/playlists/delete-song/${position}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(() => fetchCurrentPlaylist());
    }
}

// UI Updates

// Update the player status and song info
function updatePlayerStatus() {
    if (seeking || updatingVolume) return;
    
    fetchStatus().then(() => {
        // Update song position progress if playing
        if (currentStatus === 'playing' && currentSongInfo) {
            updateProgressBar();
        }
    });
}

// Update the progress bar for the current song
function updateProgressBar() {
    if (!currentSongInfo) return;
    
    const totalSeconds = parseInt(currentSongInfo.length_seconds);
    const currentSeconds = parseInt(currentSongInfo.position_seconds);
    
    if (isNaN(totalSeconds) || isNaN(currentSeconds)) return;
    
    // Update time display
    currentTime.textContent = formatTime(currentSeconds);
    totalTime.textContent = formatTime(totalSeconds);
    
    // Update progress bar
    const percentage = (currentSeconds / totalSeconds) * 100;
    progressBar.style.width = `${percentage}%`;
    seekSlider.value = percentage;
}

// Update the UI based on current state
function updateUI() {
    // Update play/pause button
    if (currentStatus === 'playing') {
        playPauseIcon.textContent = 'pause';
    } else {
        playPauseIcon.textContent = 'play_arrow';
    }
    
    // Update song info display
    if (currentSongInfo && currentSongInfo.title) {
        noSongPlaying.classList.add('hidden');
        currentSongInfoElement.classList.remove('hidden');
        
        songTitle.textContent = currentSongInfo.title || 'Unknown Title';
        songArtist.textContent = currentSongInfo.artist || 'Unknown Artist';
        songAlbum.textContent = currentSongInfo.album || '';
        
        updateProgressBar();
    } else {
        noSongPlaying.classList.remove('hidden');
        currentSongInfoElement.classList.add('hidden');
    }
}

// Update the playlists UI
function updatePlaylistsUI() {
    const renderPlaylist = (playlist) => {
        return `
            <li class="song-item ${playlist.is_current ? 'active' : ''}" 
                data-playlist-id="${playlist.id}" 
                onclick="selectPlaylist(${playlist.id})">
                <div class="flex items-center">
                    <span class="material-icons mr-2 text-gray-400">${playlist.is_current ? 'playlist_play' : 'playlist_add'}</span>
                    <span class="truncate">${playlist.name}</span>
                </div>
            </li>
        `;
    };
    
    // Render desktop playlist list
    playlistList.innerHTML = allPlaylists.map(renderPlaylist).join('');
    
    // Render mobile playlist list
    mobilePlaylistList.innerHTML = allPlaylists.map(renderPlaylist).join('');
}

// Update the now playing list
function updateNowPlayingUI(currentPosition) {
    const renderSong = (song) => {
        const isActive = parseInt(song.position) === parseInt(currentPosition);
        return `
            <li class="song-item ${isActive ? 'active' : ''}" 
                data-song-position="${song.position}" 
                onclick="playPlaylistSong(${song.position})">
                <div class="flex items-center justify-between">
                    <div class="truncate flex-1">
                        <span class="truncate block">${song.title || song.filename}</span>
                        <span class="text-xs text-gray-500">${song.length}</span>
                    </div>
                    <button class="text-gray-400 hover:text-red-500" onclick="deletePlaylistSong(${song.position}, event)">
                        <span class="material-icons text-sm">close</span>
                    </button>
                </div>
            </li>
        `;
    };
    
    // Render now playing list
    nowPlayingList.innerHTML = currentPlaylistSongs.length > 0 
        ? currentPlaylistSongs.map(renderSong).join('') 
        : '<li class="text-gray-500">No songs in playlist</li>';
}

// Update the file browser UI
function updateFileBrowserUI() {
    if (!currentDirectory) return;
    
    let html = '';
    
    // Add parent directory link if available
    if (currentDirectory.parent_directory) {
        html += `
            <div class="file-item" onclick="navigateToDirectory('${currentDirectory.parent_directory}')">
                <div class="flex items-center">
                    <span class="material-icons mr-2 text-yellow-500">arrow_upward</span>
                    <span>Parent Directory</span>
                </div>
            </div>
        `;
    }
    
    // Add directories
    currentDirectory.dirs.forEach(dir => {
        html += `
            <div class="file-item" onclick="navigateToDirectory('${dir.path}')">
                <div class="flex items-center">
                    <span class="material-icons mr-2 text-yellow-500">folder</span>
                    <span class="truncate">${dir.name}</span>
                </div>
            </div>
        `;
    });
    
    // Add files
    currentDirectory.files.forEach(file => {
        html += `
            <div class="file-item">
                <div class="flex items-center justify-between">
                    <div class="flex items-center flex-1 truncate">
                        <span class="material-icons mr-2 text-blue-500">music_note</span>
                        <span class="truncate">${file.name}</span>
                    </div>
                    <div class="flex">
                        <button class="text-gray-400 hover:text-green-500 mr-2" onclick="playFile('${file.path}')">
                            <span class="material-icons">play_arrow</span>
                        </button>
                        <button class="text-gray-400 hover:text-blue-500" onclick="addFileToPlaylist('${file.path}')">
                            <span class="material-icons">playlist_add</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    // Update desktop file browser
    fileBrowser.innerHTML = html;
    
    // Update mobile file browser
    mobileFileBrowser.innerHTML = html;
}

// Update the volume UI
function updateVolumeUI(volume) {
    if (updatingVolume) return;
    
    volume = parseInt(volume);
    if (isNaN(volume)) volume = 50;
    
    volumeSlider.value = volume;
    volumeLevel.style.width = `${volume}%`;
}

// Update the settings UI based on current settings
function updateSettingsUI(settings) {
    // Update toggle states
    setToggleState(toggleRepeat, repeatIndicator, settings.repeat);
    setToggleState(toggleShuffle, shuffleIndicator, settings.shuffle);
    setToggleState(toggleStopAfter, stopAfterIndicator, settings.stop_after);
    setToggleState(toggleAutoAdvance, autoAdvanceIndicator, settings.auto_advance);
}

// Helper Functions

// Format seconds to MM:SS
function formatTime(seconds) {
    seconds = parseInt(seconds);
    const minutes = Math.floor(seconds / 60);
    seconds = seconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Set the state of a toggle switch
function setToggleState(toggleElement, indicatorElement, isActive) {
    if (isActive) {
        toggleElement.classList.add('toggle-active');
    } else {
        toggleElement.classList.remove('toggle-active');
    }
}

// UI Controls - Modals and Dialogs

// Show the settings modal
function showSettings() {
    settingsModal.classList.remove('hidden');
}

// Hide the settings modal
function hideSettings() {
    settingsModal.classList.add('hidden');
}

// Show the mobile sidebar
function showSidebar() {
    mobileSidebar.classList.remove('hidden');
}

// Hide the mobile sidebar
function hideSidebar() {
    mobileSidebar.classList.add('hidden');
}

// Show the input dialog with title and default value
function showDialog(title, defaultValue, callback) {
    dialogTitle.textContent = title;
    dialogInput.value = defaultValue;
    
    // Store callback
    dialogConfirm.onclick = () => {
        callback(dialogInput.value);
        hideDialog();
    };
    
    // Show dialog
    inputDialog.classList.remove('hidden');
    dialogInput.focus();
}

// Hide the input dialog
function hideDialog() {
    inputDialog.classList.add('hidden');
}

// Handle the dialog confirm button
function handleDialogConfirm() {
    // The actual action is set when showing the dialog
    // This function is kept for clarity
} 